//! Test fixture producer: public package to stdout, public key/time to stderr.
use openmls::prelude::{tls_codec::*,*};
use openmls_basic_credential::SignatureKeyPair;
use openmls_rust_crypto::OpenMlsRustCrypto;
use std::io::Write;
use std::time::{SystemTime,UNIX_EPOCH};
fn main(){
    let span=std::env::args().nth(1).map(|s|s.parse::<u64>().expect("fixture span")).unwrap_or(660);
    assert!(span>60);
    let suite=Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519;
    let provider=OpenMlsRustCrypto::default();let key=SignatureKeyPair::new(suite.signature_algorithm()).unwrap();
    let mut identity=b"email-next/device/v0\0".to_vec();identity.extend_from_slice(&[1;32]);identity.extend_from_slice(&[2;32]);
    let cred=CredentialWithKey{credential:BasicCredential::new(identity).into(),signature_key:key.public().into()};
    let now=SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    let package=KeyPackage::builder().key_package_lifetime(Lifetime::init(now-60,now-60+span))
        .leaf_node_capabilities(Capabilities::builder().extensions(vec![ExtensionType::Unknown(0xff00)]).build())
        .build(suite,&provider,&key,cred).unwrap();
    let message:MlsMessageOut=package.key_package().clone().into();
    std::io::stdout().write_all(&message.tls_serialize_detached().unwrap()).unwrap();
    let hex:String=key.public().iter().map(|b|format!("{b:02x}")).collect();
    eprintln!("{hex}\n{now}");
}
