//! Two-member, locally issued-key comparison fixture. Never an incoming-mail API.
//! Stdout includes synthetic secret state and must not be logged. The lifetime
//! exception is restricted to an already-owned, originally validated package;
//! actual identities/context are independently selected fixture values.
use openmls::prelude::{tls_codec::*, *};
use openmls_basic_credential::SignatureKeyPair;
use openmls_rust_crypto::OpenMlsRustCrypto;
use openmls_traits::storage::StorageProvider;
use serde_json::{json, Value};
use std::io::{Read, Write};
const MAX: usize = 16 * 1024 * 1024;
fn now() -> u64 { std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs() }
fn hex(b: &[u8]) -> String { b.iter().map(|x| format!("{x:02x}")).collect() }
fn bytes(v: &Value) -> Result<Vec<u8>, &'static str> {
    let s = v.as_str().ok_or("hex")?;
    if s.len()%2 != 0 || !s.bytes().all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c)) { return Err("hex"); }
    s.as_bytes().chunks_exact(2).map(|c| u8::from_str_radix(std::str::from_utf8(c).unwrap(),16).map_err(|_| "hex")).collect()
}
fn checkpoint(p: &OpenMlsRustCrypto) -> Value {
    let m = p.storage().values.read().unwrap();
    let mut rows: Vec<_> = m.iter().map(|(k,v)| (hex(k),hex(v))).collect(); rows.sort(); json!(rows)
}
fn credential(p: &OpenMlsRustCrypto, a: u8, d: u8) -> (CredentialWithKey, SignatureKeyPair, Vec<u8>) {
    let mut id = b"email-next/device/v0\0".to_vec(); id.extend([a;32]); id.extend([d;32]);
    let key = SignatureKeyPair::new(SignatureScheme::ED25519).unwrap(); key.store(p.storage()).unwrap();
    (CredentialWithKey {credential:BasicCredential::new(id.clone()).into(),signature_key:key.public().into()},key,id)
}
fn fixture() -> Value {
    let a=OpenMlsRustCrypto::default(); let b=OpenMlsRustCrypto::default();
    let (ac,ak,aid)=credential(&a,1,2); let (bc,bk,bid)=credential(&b,3,4);
    let start=now(); let end=start+3; let ext=ExtensionType::Unknown(0xff00);
    let bundle=KeyPackage::builder().key_package_lifetime(Lifetime::init(start-1,end)).leaf_node_capabilities(Capabilities::builder().extensions(vec![ext]).build()).build(Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519,&b,&bk,bc).unwrap();
    let message:MlsMessageOut=bundle.key_package().clone().into(); let package=message.tls_serialize_detached().unwrap();
    let verified=match MlsMessageIn::tls_deserialize_exact(&package).unwrap().extract() { MlsMessageBodyIn::KeyPackage(k)=>k.validate(a.crypto(),ProtocolVersion::Mls10).unwrap(), _=>panic!() };
    let reference=verified.hash_ref(a.crypto()).unwrap();
    let context=b"{\"purpose\":\"delayed-welcome-fixture\"}";
    let config=MlsGroupCreateConfig::builder().ciphersuite(Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519).wire_format_policy(PURE_CIPHERTEXT_WIRE_FORMAT_POLICY).use_ratchet_tree_extension(true).with_group_context_extensions(Extensions::try_from(vec![Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ext],&[],&[CredentialType::Basic])),Extension::Unknown(0xff00,UnknownExtension(context.to_vec()))]).unwrap()).capabilities(Capabilities::new(None,None,Some(&[ext]),None,Some(&[CredentialType::Basic]))).build();
    let mut group=MlsGroup::new(&a,&ak,&config,ac).unwrap();
    let (_,welcome,_)=group.add_members(&a,&ak,&[verified]).unwrap(); group.merge_pending_commit(&a).unwrap();
    let wire=group.create_message(&a,&ak,b"An already-created encrypted message").unwrap().to_bytes().unwrap();
    json!({"checkpoint":checkpoint(&b),"key":hex(bk.public()),"identity":hex(&bid),"owner":hex(&aid),"ownerKey":hex(ak.public()),"group":hex(group.group_id().as_slice()),"context":hex(context),"reference":hex(reference.as_slice()),"sendUntil":end,"receiveUntil":end+120,"package":hex(&package),"welcome":hex(&welcome.tls_serialize_detached().unwrap()),"wire":hex(&wire)})
}
fn run(v: Value) -> Result<Value, &'static str> {
    if v["op"] == "fixture" { return Ok(fixture()); }
    if v["op"] != "strict" && v["op"] != "delayed" { return Err("operation"); }
    let p=OpenMlsRustCrypto::default();
    { let mut map=p.storage().values.write().unwrap();
      for row in v["checkpoint"].as_array().ok_or("checkpoint")? {
        if row.as_array().ok_or("row")?.len()!=2 || map.insert(bytes(&row[0])?,bytes(&row[1])?).is_some() { return Err("row"); }
      }
    }
    let welcome=match MlsMessageIn::tls_deserialize_exact(&bytes(&v["welcome"])?).map_err(|_| "welcome")?.extract() { MlsMessageBodyIn::Welcome(w)=>w, _=>return Err("welcome") };
    if welcome.secrets().len()!=1 || welcome.secrets()[0].new_member().as_slice()!=bytes(&v["reference"])? { return Err("reference"); }
    let reference=welcome.secrets()[0].new_member().clone();
    let owned:KeyPackageBundle=p.storage().key_package(&reference).map_err(|_| "storage")?.ok_or("missing-owned-package")?;
    if owned.key_package().hash_ref(p.crypto()).map_err(|_| "reference")? != reference || owned.key_package().leaf_node().signature_key().as_slice()!=bytes(&v["key"])? { return Err("owned-package"); }
    let until=v["sendUntil"].as_u64().ok_or("send deadline")?;
    if owned.key_package().life_time().not_after()!=until { return Err("original deadline"); }
    let builder=StagedWelcome::build_from_welcome(&p,&MlsGroupJoinConfig::builder().wire_format_policy(PURE_CIPHERTEXT_WIRE_FORMAT_POLICY).build(),welcome).map_err(|_| "process")?;
    let staged=if v["op"]=="delayed" {
        let retained=v["receiveUntil"].as_u64().ok_or("receive deadline")?;
        let current=now(); if retained<until || current<=until || current>retained { return Err("receive-window"); }
        builder.skip_lifetime_validation().build().map_err(|_| "stage")?
    } else { builder.build().map_err(|_| "stage")? };
    let sender=staged.welcome_sender().map_err(|_| "sender")?;
    if BasicCredential::try_from(sender.credential().clone()).map_err(|_| "sender")?.identity()!=bytes(&v["owner"])? || sender.signature_key().as_slice()!=bytes(&v["ownerKey"])? { return Err("owner"); }
    let group=staged.into_group(&p).map_err(|_| "install")?;
    if group.group_id().as_slice()!=bytes(&v["group"])? || group.extensions().unknown(0xff00).ok_or("context")?.0!=bytes(&v["context"])? || group.members().count()!=2 || BasicCredential::try_from(group.own_leaf().ok_or("own leaf")?.credential().clone()).map_err(|_| "own identity")?.identity()!=bytes(&v["identity"])? { return Err("selected group"); }
    if v["op"]=="delayed" && now()>v["receiveUntil"].as_u64().ok_or("receive deadline")? { return Err("receive-window-after-processing"); }
    let remaining:Option<KeyPackageBundle>=p.storage().key_package(&reference).map_err(|_| "storage")?;
    Ok(json!({"checkpoint":checkpoint(&p),"packageConsumed":remaining.is_none(),"group":hex(group.group_id().as_slice())}))
}
fn main() {
    let mut input=Vec::new(); std::io::stdin().take((MAX+1) as u64).read_to_end(&mut input).unwrap();
    let result=if input.len()>MAX { Err("input bound") } else { serde_json::from_slice(&input).map_err(|_| "json").and_then(run) };
    let value=match result { Ok(v)=>v,Err(reason)=>json!({"status":"worker-rejected","reason":reason}) };
    let output=serde_json::to_vec(&value).unwrap(); if output.len()>MAX { std::process::exit(2); } std::io::stdout().write_all(&output).unwrap();
}
