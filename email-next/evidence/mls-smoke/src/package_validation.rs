//! Bounded passive-discovery package checks. Caller supplies independently accepted
//! identity/key evidence and a credible time interval. This does not perform
//! identity-store authorization, package allocation/consumption or group admission.
use openmls::prelude::{tls_codec::*, *};
use openmls_rust_crypto::OpenMlsRustCrypto;

pub const MAX_PACKAGE_OCTETS: usize = 1048576;
const SUITE: Ciphersuite = Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519;

/// The returned package passed this local profile, not recipient authorization.
/// OpenMLS additionally checks lifetime against its own system clock. A caller's
/// interval cannot override that check; deployments must reconcile clock sources.
pub fn validate_discovery_package(
    bytes: &[u8], principal: &[u8; 32], device: &[u8; 32],
    accepted_signing_key: &[u8; 32], earliest: u64, latest: u64,
) -> Result<KeyPackage, &'static str> {
    if bytes.len() > MAX_PACKAGE_OCTETS { return Err("size"); }
    if principal == &[0;32] || device == &[0;32] { return Err("identifier"); }
    if earliest > latest { return Err("time-uncertain"); }
    // MLSMessage's outer ProtocolVersion is not exposed by the library API.
    // Check its fixed two-octet TLS value before parsing; the inner version is
    // independently validated by KeyPackageIn::validate below.
    if bytes.get(..2) != Some(&[0,1]) { return Err("outer-version"); }
    let message = MlsMessageIn::tls_deserialize_exact(bytes).map_err(|_| "tls")?;
    let incoming = match message.extract() {
        MlsMessageBodyIn::KeyPackage(package) => package,
        _ => return Err("wire-format"),
    };
    let provider = OpenMlsRustCrypto::default();
    let package = incoming.validate(provider.crypto(), ProtocolVersion::Mls10)
        .map_err(|_| "mls-validation")?;
    if package.ciphersuite() != SUITE { return Err("suite"); }
    if package.last_resort() { return Err("last-resort"); }
    let leaf = package.leaf_node();
    let credential = BasicCredential::try_from(leaf.credential().clone()).map_err(|_| "credential-type")?;
    let mut expected = b"email-next/device/v0\0".to_vec();
    expected.extend_from_slice(principal); expected.extend_from_slice(device);
    if credential.identity() != expected { return Err("credential-identity"); }
    if leaf.signature_key().as_slice() != accepted_signing_key { return Err("signing-key"); }
    let lifetime = package.life_time();
    let before = lifetime.not_before(); let after = lifetime.not_after();
    if after < before || after-before > 604800 { return Err("lifetime-span"); }
    if earliest < before || latest > after { return Err("lifetime-interval"); }
    let caps = leaf.capabilities();
    if !caps.versions().contains(&ProtocolVersion::Mls10)
        || !caps.ciphersuites().contains(&SUITE.into())
        || !caps.credentials().contains(&CredentialType::Basic)
        || !caps.extensions().contains(&ExtensionType::Unknown(0xff00)) {
        return Err("required-capabilities");
    }
    // Advertising the private-use extension does not prove its implementation.
    Ok(package)
}

#[cfg(test)]
mod tests {
    use super::*;
    use openmls_basic_credential::SignatureKeyPair;
    use std::time::{SystemTime, UNIX_EPOCH};
    fn fixture(extension: bool, span: u64, suite: Ciphersuite) -> (Vec<u8>, [u8;32], u64) {
        let provider=OpenMlsRustCrypto::default();
        let key=SignatureKeyPair::new(suite.signature_algorithm()).unwrap();
        let mut identity=b"email-next/device/v0\0".to_vec();
        identity.extend_from_slice(&[1;32]);identity.extend_from_slice(&[2;32]);
        let credential=CredentialWithKey {credential:BasicCredential::new(identity).into(),signature_key:key.public().into()};
        let now=SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let caps=Capabilities::builder().extensions(if extension {vec![ExtensionType::Unknown(0xff00)]} else {vec![]}).build();
        let package=KeyPackage::builder().key_package_lifetime(Lifetime::init(now-60,now-60+span))
            .leaf_node_capabilities(caps).build(suite,&provider,&key,credential).unwrap();
        let message:MlsMessageOut=package.key_package().clone().into();
        (message.tls_serialize_detached().unwrap(),key.public().try_into().unwrap(),now)
    }
    fn check(b:&[u8],k:&[u8;32],n:u64)->Result<KeyPackage,&'static str> {
        validate_discovery_package(b,&[1;32],&[2;32],k,n,n+1)
    }
    #[test]
    fn exact_mls_message_validates_and_reference_uses_library() {
        let (b,k,n)=fixture(true,604800,SUITE);
        let package=check(&b,&k,n).unwrap();
        assert!(package.hash_ref(OpenMlsRustCrypto::default().crypto()).is_ok());
        let mut trailing=b.clone();trailing.push(0);assert_eq!(check(&trailing,&k,n).unwrap_err(),"tls");
        let raw=package.tls_serialize_detached().unwrap();assert!(check(&raw,&k,n).is_err());
    }
    #[test]
    fn wrong_identity_key_signature_and_versions_fail() {
        let (b,k,n)=fixture(true,604800,SUITE);
        assert_eq!(validate_discovery_package(&b,&[3;32],&[2;32],&k,n,n).unwrap_err(),"credential-identity");
        assert_eq!(validate_discovery_package(&b,&[1;32],&[3;32],&k,n,n).unwrap_err(),"credential-identity");
        assert_eq!(check(&b,&[9;32],n).unwrap_err(),"signing-key");
        let mut altered=b.clone();*altered.last_mut().unwrap()^=1;assert_eq!(check(&altered,&k,n).unwrap_err(),"mls-validation");
        let mut outer=b.clone();outer[1]=2;assert_eq!(check(&outer,&k,n).unwrap_err(),"outer-version");
        let mut inner=b.clone();inner[5]=2;assert!(check(&inner,&k,n).is_err());
    }
    #[test]
    fn profile_lifetime_capability_and_bounds_fail() {
        let (b,k,n)=fixture(false,604800,SUITE);assert_eq!(check(&b,&k,n).unwrap_err(),"required-capabilities");
        let (b,k,n)=fixture(true,604801,SUITE);assert_eq!(check(&b,&k,n).unwrap_err(),"lifetime-span");
        let (b,k,n)=fixture(true,604800,SUITE);
        assert_eq!(validate_discovery_package(&b,&[1;32],&[2;32],&k,n-61,n).unwrap_err(),"lifetime-interval");
        assert_eq!(validate_discovery_package(&b,&[1;32],&[2;32],&k,n,n+604800).unwrap_err(),"lifetime-interval");
        assert_eq!(validate_discovery_package(&b,&[1;32],&[2;32],&k,n+1,n).unwrap_err(),"time-uncertain");
        assert_eq!(check(&vec![0;MAX_PACKAGE_OCTETS+1],&k,n).unwrap_err(),"size");
        let (b,k,n)=fixture(true,604800,Ciphersuite::MLS_128_DHKEMX25519_CHACHA20POLY1305_SHA256_Ed25519);
        assert_eq!(check(&b,&k,n).unwrap_err(),"suite");
    }
}
