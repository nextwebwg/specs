//! Fixed RFC9180 Base-mode control envelope; local test keys stay on stdin/stdout.
//! No sender authentication, identity admission, publication or release permission.
use openmls::prelude::OpenMlsProvider;
use openmls_rust_crypto::OpenMlsRustCrypto;
use openmls_traits::{crypto::OpenMlsCrypto,random::OpenMlsRand,types::*};
use serde_json::{json,Value};
use std::io::{Read,Write};
const MAGIC:&[u8;8]=b"EML2CTL0";
const INFO:&[u8]=b"email2/sealed-control/v0\0";
const MAX:usize=8*1024*1024;
fn hex(b:&[u8])->String{b.iter().map(|c|format!("{c:02x}")).collect()}
fn bytes(v:&Value,k:&str)->Result<Vec<u8>,&'static str>{let s=v[k].as_str().ok_or("hex")?;if s.len()%2!=0||!s.bytes().all(|c|c.is_ascii_digit()||(b'a'..=b'f').contains(&c)){return Err("hex");}s.as_bytes().chunks_exact(2).map(|b|u8::from_str_radix(std::str::from_utf8(b).unwrap(),16).map_err(|_|"hex")).collect()}
fn config()->HpkeConfig{HpkeConfig(HpkeKemType::DhKem25519,HpkeKdfType::HkdfSha256,HpkeAeadType::AesGcm128)}
fn run(v:Value)->Result<Value,&'static str>{
 let p=OpenMlsRustCrypto::default();let op=v["op"].as_str().ok_or("op")?;
 if op=="generate"{let ikm=p.rand().random_array::<32>().map_err(|_|"random")?;let key=p.crypto().derive_hpke_keypair(config(),&ikm).map_err(|_|"keygen")?;let id=loop{let candidate=p.rand().random_array::<16>().map_err(|_|"random")?;if candidate.iter().any(|v|*v!=0){break candidate;}};return Ok(json!({"id":hex(&id),"publicKey":hex(&key.public),"privateKey":hex(&key.private)}));}
 let id=bytes(&v,"id")?;let public=bytes(&v,"publicKey")?;
 if id.len()!=16||id.iter().all(|v|*v==0)||public.len()!=32{return Err("key fields");}
 let mut info=INFO.to_vec();info.extend_from_slice(&id);info.extend_from_slice(&public);
 if op=="seal"{
  let plain=bytes(&v,"plaintext")?;if plain.len()>MAX{return Err("plaintext bound");}
  let length=u32::try_from(plain.len()+16).map_err(|_|"length")?;
  let mut aad=MAGIC.to_vec();aad.extend_from_slice(&id);aad.extend_from_slice(&length.to_be_bytes());
  let sealed=p.crypto().hpke_seal(config(),&public,&info,&aad,&plain).map_err(|_|"seal")?;
  if sealed.kem_output.as_slice().len()!=32||sealed.ciphertext.as_slice().len()!=length as usize{return Err("backend format");}
  let mut wire=MAGIC.to_vec();wire.extend_from_slice(&id);wire.extend_from_slice(sealed.kem_output.as_slice());wire.extend_from_slice(&length.to_be_bytes());wire.extend_from_slice(sealed.ciphertext.as_slice());
  return Ok(json!({"ciphertext":hex(&wire)}));
 }
 if op!="open"{return Err("op");}
 let wire=bytes(&v,"ciphertext")?;let private=bytes(&v,"privateKey")?;
 if private.len()!=32||wire.len()<76||wire.len()>MAX+76||&wire[..8]!=MAGIC||wire[8..24]!=id{return Err("envelope");}
 let length=u32::from_be_bytes(wire[56..60].try_into().unwrap()) as usize;
 if length<16||length!=wire.len()-60{return Err("length");}
 let mut aad=MAGIC.to_vec();aad.extend_from_slice(&id);aad.extend_from_slice(&wire[56..60]);
 let input=HpkeCiphertext{kem_output:wire[24..56].to_vec().into(),ciphertext:wire[60..].to_vec().into()};
 let plain=p.crypto().hpke_open(config(),&input,&private,&info,&aad).map_err(|_|"authentication")?;
 Ok(json!({"plaintext":hex(&plain)}))
}
fn main(){let mut raw=Vec::new();std::io::stdin().take((MAX*3+1024) as u64).read_to_end(&mut raw).unwrap();let result=if raw.len()>MAX*3{Err("input bound")}else{serde_json::from_slice(&raw).map_err(|_|"json").and_then(run)};let output=serde_json::to_vec(&match result{Ok(v)=>v,Err(e)=>json!({"status":"rejected","reason":e})}).unwrap();std::io::stdout().write_all(&output).unwrap();}
