//! Local trusted orchestration worker. Output contains secrets; never log it.
use openmls::prelude::{tls_codec::*,*};
use openmls_basic_credential::SignatureKeyPair;
use openmls_rust_crypto::OpenMlsRustCrypto;
use openmls_traits::signatures::Signer;
use openmls_traits::storage::StorageProvider;
use serde_json::{json,Value};
use std::io::{Read,Write};
const MAX:usize=16*1024*1024;
fn hex(b:&[u8])->String{b.iter().map(|x|format!("{x:02x}")).collect()}
fn bytes(v:&Value,k:&str)->Vec<u8>{let s=v[k].as_str().unwrap();assert!(s.len()%2==0&&s.bytes().all(|c|c.is_ascii_digit()||(b'a'..=b'f').contains(&c)));s.as_bytes().chunks_exact(2).map(|c|u8::from_str_radix(std::str::from_utf8(c).unwrap(),16).unwrap()).collect()}
fn checkpoint(p:&OpenMlsRustCrypto)->Value{let map=p.storage().values.read().unwrap();let mut rows:Vec<_>=map.iter().map(|(k,v)|(hex(k),hex(v))).collect();rows.sort();json!(rows)}
fn run(v:Value)->Value{
 let p=OpenMlsRustCrypto::default();
 if let Some(rows)=v["checkpoint"].as_array(){let mut map=p.storage().values.write().unwrap();for row in rows{let k=bytes(&json!({"v":row[0]}),"v");let b=bytes(&json!({"v":row[1]}),"v");assert!(map.insert(k,b).is_none());}}
 let suite=Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519;
 let op=v["op"].as_str().unwrap();
 if op=="prepare"{
  let identity=bytes(&v,"identity");assert!(identity.len()==85&&identity.starts_with(b"email-next/device/v0\0"));
  let key=SignatureKeyPair::new(SignatureScheme::ED25519).unwrap();key.store(p.storage()).unwrap();
  let cred=CredentialWithKey{credential:BasicCredential::new(identity).into(),signature_key:key.public().into()};
  let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
  let bundle=KeyPackage::builder().key_package_lifetime(Lifetime::init(now-60,now+600)).leaf_node_capabilities(Capabilities::builder().extensions(vec![ExtensionType::Unknown(0xff00)]).build()).build(suite,&p,&key,cred).unwrap();
  let reference=bundle.key_package().hash_ref(p.crypto()).unwrap();
  let message:MlsMessageOut=bundle.key_package().clone().into();
  return json!({"checkpoint":checkpoint(&p),"key":hex(key.public()),"package":hex(&message.tls_serialize_detached().unwrap()),"reference":hex(reference.as_slice()),"time":now});
 }
 let key=SignatureKeyPair::read(p.storage(),&bytes(&v,"key"),SignatureScheme::ED25519).unwrap();
 if op=="package-reference"{
  let package=match MlsMessageIn::tls_deserialize_exact(&bytes(&v,"package")).unwrap().extract(){MlsMessageBodyIn::KeyPackage(k)=>k.validate(p.crypto(),ProtocolVersion::Mls10).unwrap(),_=>panic!()};
  return json!({"reference":hex(package.hash_ref(p.crypto()).unwrap().as_slice())});
 }
 if op=="fresh-package"{
  // Isolated key/package provider: no prior group ratchets copied into admission.
  let fresh=OpenMlsRustCrypto::default();key.store(fresh.storage()).unwrap();
  let identity=bytes(&v,"identity");assert!(identity.len()==85&&identity.starts_with(b"email-next/device/v0\0"));
  let cred=CredentialWithKey{credential:BasicCredential::new(identity).into(),signature_key:key.public().into()};
  let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
  let bundle=KeyPackage::builder().key_package_lifetime(Lifetime::init(now-60,now+600)).leaf_node_capabilities(Capabilities::builder().extensions(vec![ExtensionType::Unknown(0xff00)]).build()).build(suite,&fresh,&key,cred).unwrap();
  let reference=bundle.key_package().hash_ref(fresh.crypto()).unwrap();let message:MlsMessageOut=bundle.key_package().clone().into();
  return json!({"checkpoint":checkpoint(&fresh),"key":hex(key.public()),"package":hex(&message.tls_serialize_detached().unwrap()),"reference":hex(reference.as_slice()),"time":now});
 }
 if op=="sign"{
  let domain=v["domain"].as_str().unwrap();assert!(["email2/pairing-setup/request/v0","email2/pairing-setup/response/v0","email2/pairing-setup/receipt/v0","email-next/mls-established-membership-invitation/v6","email-next/service-account-link/v0","email-next/passive-discovery/v6","email-next/passive-discovery/v7","email-next/mls-initial-roster/v4","email-next/mls-new-conversation-invitation/v7","email-next/mls-established-membership-invitation/v7","email-next/mls-new-conversation-invitation/v6","email-next/mls-initial-roster/v3","email-next/ordering-experiment/proposal/v0","email-next/ordering-experiment/prepare/v0","email-next/ordering-experiment/prepared/v0","email-next/ordering-experiment/commit/v0","email-next/ordering-experiment/decision/v0","email-next/ordering-experiment/report/v0","email-next/ordering-experiment/new-view/v0","email-next/ordering-experiment/admin-intent/v0","email-next/device-binding/v0","email-next/device-possession/v0","email-next/identity-state/v0","email-next/passive-discovery/v0","email-next/passive-discovery/v1", "email-next/passive-discovery/v2","email-next/passive-discovery/v3","email-next/passive-discovery/v4","email-next/passive-discovery/v5","email-next/mls-new-conversation-invitation/v5","email-next/mls-initial-roster/v2","email-next/mls-established-membership-invitation/v5","email-next/provider-control/v0","email-next/mls-new-conversation-invitation/v0","email-next/mls-new-conversation-invitation/v1", "email-next/mls-new-conversation-invitation/v2","email-next/mls-established-membership-invitation/v0","email-next/mls-established-membership-invitation/v1","email-next/mls-established-membership-invitation/v2","email-next/mls-established-membership-invitation/v3","email-next/mls-initial-roster/v0","email-next/mls-new-conversation-invitation/v3","email-next/mls-new-conversation-invitation/v4","email-next/mls-initial-roster/v1","email-next/mls-established-membership-invitation/v4"].contains(&domain));
  let payload=bytes(&v,"payload");let mut input=domain.as_bytes().to_vec();input.push(0);input.extend((payload.len()as u32).to_be_bytes());input.extend(payload);
  return json!({"signature":hex(&key.sign(&input).unwrap())});
 }
 if op=="create-initial-roster"{
  let app_context=bytes(&v,"context");assert!(app_context.len()<=65536);
  let packages=v["packages"].as_array().unwrap().iter().map(|x|match MlsMessageIn::tls_deserialize_exact(&bytes(&json!({"p":x}),"p")).unwrap().extract(){MlsMessageBodyIn::KeyPackage(k)=>k.validate(p.crypto(),ProtocolVersion::Mls10).unwrap(),_=>panic!()}).collect::<Vec<_>>();assert!(!packages.is_empty());
  let mut references=packages.iter().map(|k|hex(k.hash_ref(p.crypto()).unwrap().as_slice())).collect::<Vec<_>>();references.sort();assert!(references.windows(2).all(|w|w[0]!=w[1]));
  let ext=ExtensionType::Unknown(0xff00);let config=MlsGroupCreateConfig::builder().ciphersuite(suite).use_ratchet_tree_extension(true).with_group_context_extensions(Extensions::try_from(vec![Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ext],&[],&[CredentialType::Basic])),Extension::Unknown(0xff00,UnknownExtension(app_context))]).unwrap()).capabilities(Capabilities::new(None,None,Some(&[ext]),None,Some(&[CredentialType::Basic]))).build();
  let mut group=MlsGroup::new(&p,&key,&config,CredentialWithKey{credential:BasicCredential::new(bytes(&v,"identity")).into(),signature_key:key.public().into()}).unwrap();
  let(_,welcome,_)=group.add_members(&p,&key,&packages).unwrap();group.merge_pending_commit(&p).unwrap();
  let exported=group.export_group_info(p.crypto(),&key,false).unwrap();let info=match MlsMessageIn::tls_deserialize_exact(&exported.tls_serialize_detached().unwrap()).unwrap().extract(){MlsMessageBodyIn::GroupInfo(i)=>i,_=>panic!()};
  return json!({"checkpoint":checkpoint(&p),"group":hex(group.group_id().as_slice()),"epoch":group.epoch().as_u64().to_string(),"context":hex(&group.extensions().unknown(0xff00).unwrap().0),"groupContext":hex(&info.group_context().tls_serialize_detached().unwrap()),"welcome":hex(&welcome.tls_serialize_detached().unwrap()),"references":references,"members":group.members().map(|m|json!({"identity":hex(BasicCredential::try_from(m.credential).unwrap().identity()),"key":hex(&m.signature_key)})).collect::<Vec<_>>()});
 }
 if op=="invite" || op=="invite-fixture-context" || op=="create-initial-application"{
  // Internal creation primitive; caller validates policy/context. Never admission.
  let app_context=if op=="invite-fixture-context" || op=="create-initial-application"{let c=bytes(&v,"context");assert!(c.len()<=65536);c}else{include_bytes!("../../fixtures/context.json").to_vec()};
  let message=MlsMessageIn::tls_deserialize_exact(&bytes(&v,"package")).unwrap();
  let package=match message.extract(){MlsMessageBodyIn::KeyPackage(k)=>k.validate(p.crypto(),ProtocolVersion::Mls10).unwrap(),_=>panic!()};
  let reference=package.hash_ref(p.crypto()).unwrap();let ext=ExtensionType::Unknown(0xff00);
  let config=MlsGroupCreateConfig::builder().ciphersuite(suite).use_ratchet_tree_extension(v["embedded"].as_bool().unwrap_or(false)).with_group_context_extensions(Extensions::try_from(vec![Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ext],&[],&[CredentialType::Basic])),Extension::Unknown(0xff00,UnknownExtension(app_context))]).unwrap()).capabilities(Capabilities::new(None,None,Some(&[ext]),None,Some(&[CredentialType::Basic]))).build();
  let cred=CredentialWithKey{credential:BasicCredential::new(bytes(&v,"identity")).into(),signature_key:key.public().into()};
  let mut group=MlsGroup::new(&p,&key,&config,cred).unwrap();let(_,welcome,_)=group.add_members(&p,&key,&[package]).unwrap();group.merge_pending_commit(&p).unwrap();
  return json!({"checkpoint":checkpoint(&p),"group":hex(group.group_id().as_slice()),"welcome":hex(&welcome.tls_serialize_detached().unwrap()),"tree":hex(&group.export_ratchet_tree().tls_serialize_detached().unwrap()),"reference":hex(reference.as_slice()),"authenticator":hex(group.epoch_authenticator().as_slice())});
 }
 if op=="join" || op=="join-embedded" || op=="join-initial-roster"{
  let welcome=match MlsMessageIn::tls_deserialize_exact(&bytes(&v,"welcome")).unwrap().extract(){MlsMessageBodyIn::Welcome(w)=>w,_=>panic!()};
  let staged=if op=="join-embedded" || op=="join-initial-roster"{
   if op=="join-embedded"{assert!(welcome.secrets().len()==1 && welcome.secrets()[0].new_member().as_slice()==bytes(&v,"reference"));}
   else{
    let target=bytes(&v,"reference");let mut actual=welcome.secrets().iter().map(|s|hex(s.new_member().as_slice())).collect::<Vec<_>>();actual.sort();
    let expected=v["references"].as_array().unwrap().iter().map(|s|s.as_str().unwrap().to_string()).collect::<Vec<_>>();assert!(!expected.is_empty()&&actual==expected&&actual.windows(2).all(|w|w[0]!=w[1]));
    let mut found=0;for secret in welcome.secrets(){let stored:Option<KeyPackageBundle>=p.storage().key_package(&secret.new_member()).unwrap();if stored.is_some(){assert!(secret.new_member().as_slice()==target);found+=1;}}assert_eq!(found,1);
   }
   let processed=ProcessedWelcome::new_from_welcome(&p,&MlsGroupJoinConfig::default(),welcome).unwrap();
   assert!(processed.psks().is_empty());
   assert!(processed.unverified_group_info().extensions().ratchet_tree().is_some());
   processed.into_staged_welcome(&p,None).unwrap()
  }else{
   let tree=RatchetTreeIn::tls_deserialize_exact(&bytes(&v,"tree")).unwrap();
   StagedWelcome::new_from_welcome(&p,&MlsGroupJoinConfig::default(),welcome,Some(tree)).unwrap()
  };
  let sender=staged.welcome_sender().unwrap();
  let sender_identity=hex(BasicCredential::try_from(sender.credential().clone()).unwrap().identity());
  let sender_key=hex(sender.signature_key().as_slice());
  let group=staged.into_group(&p).unwrap();
  if op=="join-initial-roster"{let own=group.own_leaf().unwrap();assert_eq!(BasicCredential::try_from(own.credential().clone()).unwrap().identity(),bytes(&v,"identity"));assert_eq!(own.signature_key().as_slice(),key.public());}
  let exported=group.export_group_info(p.crypto(),&key,false).unwrap();
  let info=match MlsMessageIn::tls_deserialize_exact(&exported.tls_serialize_detached().unwrap()).unwrap().extract(){MlsMessageBodyIn::GroupInfo(i)=>i,_=>panic!()};
  let finalized=hex(&info.group_context().tls_serialize_detached().unwrap());
  return json!({"checkpoint":checkpoint(&p),"group":hex(group.group_id().as_slice()),"groupContext":finalized,"signerIdentity":sender_identity,"signerKey":sender_key,"epoch":group.epoch().as_u64().to_string(),"context":hex(&group.extensions().unknown(0xff00).unwrap().0),"members":group.members().map(|m|json!({"identity":hex(BasicCredential::try_from(m.credential).unwrap().identity()),"key":hex(&m.signature_key)})).collect::<Vec<_>>(),"authenticator":hex(group.epoch_authenticator().as_slice())});
 }
 let mut group=MlsGroup::load(p.storage(),&GroupId::from_slice(&bytes(&v,"group"))).unwrap().unwrap();
 // This metadata comes from the loaded authenticated group, not a caller roster.
 let own=group.own_leaf().unwrap();
 assert_eq!(own.signature_key().as_slice(),key.public());
 let metadata=json!({"group":hex(group.group_id().as_slice()),"epoch":group.epoch().as_u64().to_string(),"context":hex(&group.extensions().unknown(0xff00).unwrap().0),"senderIdentity":hex(BasicCredential::try_from(own.credential().clone()).unwrap().identity()),"senderKey":hex(key.public()),"members":group.members().map(|m|json!({"identity":hex(BasicCredential::try_from(m.credential).unwrap().identity()),"key":hex(&m.signature_key)})).collect::<Vec<_>>()});
 if op=="inspect-send"{return json!({"metadata":metadata});}
 if op=="send"{group.set_aad(vec![]);let wire=group.create_message(&p,&key,&bytes(&v,"application")).unwrap().to_bytes().unwrap();return json!({"checkpoint":checkpoint(&p),"wire":hex(&wire),"metadata":metadata});}
 panic!("unsupported local operation")
}
fn main(){std::panic::set_hook(Box::new(|_|{}));let mut input=Vec::new();std::io::stdin().take((MAX+1)as u64).read_to_end(&mut input).unwrap();if input.len()>MAX{std::process::exit(2)}let result=std::panic::catch_unwind(||run(serde_json::from_slice(&input).unwrap()));let output=serde_json::to_vec(&result.unwrap_or_else(|_|json!({"status":"worker-rejected"}))).unwrap();if output.len()>MAX{std::process::exit(2)}std::io::stdout().write_all(&output).unwrap();}
