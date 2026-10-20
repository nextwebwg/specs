//! Fixed, public local-test transcript with real package and application proofs.
//! No private key export, user input, identity acceptance or production signing API.
use openmls::prelude::{tls_codec::*,*};
use openmls_basic_credential::SignatureKeyPair;
use openmls_traits::signatures::Signer;
use openmls_rust_crypto::OpenMlsRustCrypto;
use std::time::{SystemTime,UNIX_EPOCH};
use std::process::Command;
fn hex(b:&[u8])->String{b.iter().map(|v|format!("{v:02x}")).collect()}
fn b64(b:&[u8])->String{
    const A:&[u8]=b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut s=String::new();for c in b.chunks(3){let n=((c[0] as u32)<<16)|((c.get(1).copied().unwrap_or(0) as u32)<<8)|c.get(2).copied().unwrap_or(0) as u32;
        s.push(A[((n>>18)&63) as usize] as char);s.push(A[((n>>12)&63) as usize] as char);
        s.push(if c.len()>1{A[((n>>6)&63) as usize] as char}else{'='});s.push(if c.len()>2{A[(n&63) as usize] as char}else{'='});}s
}
fn proof(key:&SignatureKeyPair,domain:&str,payload:&[u8])->String{
    let mut b=domain.as_bytes().to_vec();b.push(0);b.extend_from_slice(&(payload.len() as u32).to_be_bytes());b.extend_from_slice(payload);hex(&key.sign(&b).unwrap())
}
fn main(){
    let suite=Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519;
    let provider=OpenMlsRustCrypto::default();let key=SignatureKeyPair::new(suite.signature_algorithm()).unwrap();
    let mut identity=b"email-next/device/v0\0".to_vec();identity.extend_from_slice(&[1;32]);identity.extend_from_slice(&[2;32]);
    let cred=CredentialWithKey{credential:BasicCredential::new(identity.clone()).into(),signature_key:key.public().into()};
    let now=SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    let bundle=KeyPackage::builder().key_package_lifetime(Lifetime::init(now-60,now+600))
        .leaf_node_capabilities(Capabilities::builder().extensions(vec![ExtensionType::Unknown(0xff00)]).build())
        .build(suite,&provider,&key,cred).unwrap();
    let message:MlsMessageOut=bundle.key_package().clone().into();let package=message.tls_serialize_detached().unwrap();
    // Reuse the existing fixed identity fixture's exact JSON encoding and SHA256 references.
    let script=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../mls_identity.py");
    let output=Command::new(std::env::var("EMAIL_NEXT_PYTHON").unwrap_or_else(|_|"python3".into())).arg(script).args(["prepare",&hex(&identity),&hex(key.public()),&now.to_string()]).output().unwrap();
    assert!(output.status.success());let text=String::from_utf8(output.stdout).unwrap();let lines:Vec<_>=text.lines().collect();
    let unhex=|s:&str|->Vec<u8>{s.as_bytes().chunks_exact(2).map(|v|u8::from_str_radix(std::str::from_utf8(v).unwrap(),16).unwrap()).collect()};
    let binding=unhex(lines[0]);let state=unhex(lines[1]);
    // OpenMLS provider supplies the already selected SHA256 implementation.
    let digest=|b:&[u8]|hex(&provider.crypto().hash(openmls_traits::types::HashType::Sha2_256,b).unwrap());
    let principal=format!("enp0:{}","01".repeat(32));let device=format!("end0:{}","02".repeat(32));
    let assertion=format!("{{\"version\":\"0\",\"purpose\":\"passive-discovery\",\"record\":\"{}\",\"principal\":\"{principal}\",\"device\":\"{device}\",\"state\":\"{}\",\"binding\":\"{}\",\"mailbox\":\"Alice@example.com\",\"notBefore\":\"{}\",\"notAfter\":\"{}\",\"features\":[\"mls-1-0001\"],\"keyPackage\":[\"{}\"]}}","3".repeat(32),digest(&state),digest(&binding),now-60,now+600,b64(&package));
    let authorization=proof(&key,"email-next/device-binding/v0",&binding);let possession=proof(&key,"email-next/device-possession/v0",&binding);let state_proof=proof(&key,"email-next/identity-state/v0",&state);
    println!("{{\"binding\":\"{}\",\"state\":\"{}\",\"authorization\":\"{authorization}\",\"possession\":\"{possession}\",\"stateProof\":\"{state_proof}\",\"assertion\":\"{}\",\"signature\":\"{}\",\"time\":\"{now}\"}}",b64(&binding),b64(&state),b64(assertion.as_bytes()),proof(&key,"email-next/passive-discovery/v0",assertion.as_bytes()));
}
