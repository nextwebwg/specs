//! Local bounded staging worker. Stdout contains secret state: never log it.
use openmls::prelude::{tls_codec::*,*};
use openmls_basic_credential::SignatureKeyPair;
use openmls_rust_crypto::OpenMlsRustCrypto;
use openmls_traits::signatures::Signer;
use serde_json::{json,Value};
use std::io::{Read,Write};
const MAX:usize=16*1024*1024;
fn hex(b:&[u8])->String{b.iter().map(|x|format!("{x:02x}")).collect()}
fn unhex(s:&str)->Result<Vec<u8>,String>{if s.len()%2!=0 || !s.bytes().all(|b|b.is_ascii_digit()||(b'a'..=b'f').contains(&b)){return Err("hex".into())}s.as_bytes().chunks_exact(2).map(|c|u8::from_str_radix(std::str::from_utf8(c).unwrap(),16).map_err(|_|"hex".into())).collect()}
fn text<'a>(v:&'a Value,k:&str)->Result<&'a str,String>{v.get(k).and_then(Value::as_str).ok_or(k.into())}
fn checkpoint(p:&OpenMlsRustCrypto)->Value{let values=p.storage().values.read().unwrap();let mut entries:Vec<_>=values.iter().map(|(k,v)|(hex(k),hex(v))).collect();entries.sort();json!(entries)}
fn snapshot(g:&MlsGroup)->Value{json!({"group":hex(g.group_id().as_slice()),"epoch":g.epoch().as_u64().to_string(),"context":hex(&g.extensions().unknown(0xff00).unwrap().0),"members":g.members().map(|m|format!("{}:{}:{}",m.index.u32(),hex(BasicCredential::try_from(m.credential).unwrap().identity()),hex(&m.signature_key))).collect::<Vec<_>>()})}
fn receive(v:Value)->Result<Value,String>{
 if v["format"]!="openmls-0.9.1-map-0"{return Err("format".into())}
 let p=OpenMlsRustCrypto::default();{
 let mut map=p.storage().values.write().unwrap();
 for row in v["checkpoint"].as_array().ok_or("checkpoint")?{let a=row.as_array().ok_or("entry")?;if a.len()!=2{return Err("entry".into())}let k=unhex(a[0].as_str().ok_or("key")?)?;let b=unhex(a[1].as_str().ok_or("value")?)?;if map.insert(k,b).is_some(){return Err("duplicate-key".into())}}
 }
 let id=GroupId::from_slice(&unhex(text(&v,"group")?)?);
 let mut group=MlsGroup::load(p.storage(),&id).map_err(|_|"load")?.ok_or("missing-group")?;
 let context=snapshot(&group); // bounded first stage: current accepted epoch only
 let wire=unhex(text(&v,"wire")?)?;
 let msg=MlsMessageIn::tls_deserialize_exact(&wire).map_err(|_|"framing")?;
 if msg.wire_format()!=WireFormat::PrivateMessage{return Err("not-private".into())}
 let protocol=msg.try_into_protocol_message().map_err(|_|"not-protocol")?;
 let processed=group.process_message(&p,protocol).map_err(|_|"crypto-rejected")?;
 let historical=processed.epoch()!=group.epoch();
 if historical && v["allowHistorical"]!=true{return Err("historical-epoch-unsupported".into())}
 let sender=match processed.sender(){Sender::Member(i)=>i.u32().to_string(),_=>return Err("not-member".into())};
 let credential=hex(BasicCredential::try_from(processed.credential().clone()).map_err(|_|"credential")?.identity());
 let metadata=json!({"group":hex(processed.group_id().as_slice()),"epoch":processed.epoch().as_u64().to_string(),"sender":sender,"credential":credential,"aad":hex(processed.aad())});
 let bytes=match processed.into_content(){ProcessedMessageContent::ApplicationMessage(m)=>m.into_bytes(),_=>return Err("not-application".into())};
 Ok(json!({"status":"authenticated-application","checkpoint":checkpoint(&p),"snapshot":if historical{Value::Null}else{context},"historical":historical,"processed":metadata,"application":hex(&bytes)}))
}
fn credential(p:&OpenMlsRustCrypto,a:u8,d:u8)->(CredentialWithKey,SignatureKeyPair){let mut id=b"email-next/device/v0\0".to_vec();id.extend([a;32]);id.extend([d;32]);let k=SignatureKeyPair::new(SignatureScheme::ED25519).unwrap();k.store(p.storage()).unwrap();(CredentialWithKey{credential:BasicCredential::new(id).into(),signature_key:k.public().into()},k)}
fn fixture()->Value{
 let a=OpenMlsRustCrypto::default();let b=OpenMlsRustCrypto::default();let(ac,ak)=credential(&a,1,2);let(bc,bk)=credential(&b,3,4);
 let ext=ExtensionType::Unknown(0xff00);
 let kp=KeyPackage::builder().leaf_node_capabilities(Capabilities::builder().extensions(vec![ext]).build()).build(Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519,&b,&bk,bc).unwrap();
 let config=MlsGroupCreateConfig::builder().ciphersuite(Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519).with_group_context_extensions(Extensions::try_from(vec![Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ext],&[],&[CredentialType::Basic])),Extension::Unknown(0xff00,UnknownExtension(include_bytes!("../../fixtures/context.json").to_vec()))]).unwrap()).capabilities(Capabilities::new(None,None,Some(&[ext]),None,Some(&[CredentialType::Basic]))).build();
 let mut alice=MlsGroup::new(&a,&ak,&config,ac).unwrap();let(_,welcome,_)=alice.add_members(&a,&ak,&[kp.key_package().clone()]).unwrap();alice.merge_pending_commit(&a).unwrap();
 let welcome=match MlsMessageIn::tls_deserialize_exact(&welcome.tls_serialize_detached().unwrap()).unwrap().extract(){MlsMessageBodyIn::Welcome(w)=>w,_=>panic!()};
 let bob=StagedWelcome::new_from_welcome(&b,&MlsGroupJoinConfig::default(),welcome,Some(alice.export_ratchet_tree().into())).unwrap().into_group(&b).unwrap();
 let initial=checkpoint(&b);let payload=include_bytes!("../../fixtures/message.json");
 let mut wires=Vec::new();for bytes in [payload.as_slice(),payload.as_slice(),b"invalid-json".as_slice()]{wires.push(hex(&alice.create_message(&a,&ak,bytes).unwrap().to_bytes().unwrap()))}
 let mut collision:Value=serde_json::from_slice(payload).unwrap();collision["operation"]["text"]=json!("Conflicting authenticated content");
 wires.push(hex(&alice.create_message(&a,&ak,&serde_json::to_vec(&collision).unwrap()).unwrap().to_bytes().unwrap()));
 let mut question:Value=serde_json::from_slice(payload).unwrap();question["event"]=json!("5".repeat(32));question["operation"]=json!({"kind":"question","text":"Which day?","options":[{"id":"7".repeat(32),"label":"Thursday"}]});
 let mut answer=question.clone();answer["event"]=json!("6".repeat(32));answer["operation"]=json!({"kind":"answer","question":{"principal":question["principal"],"conversation":question["conversation"],"event":question["event"]},"option":"7".repeat(32),"replaces":[]});
 for event in [&answer,&question,&answer]{wires.push(hex(&alice.create_message(&a,&ak,&serde_json::to_vec(event).unwrap()).unwrap().to_bytes().unwrap()));}
 let mut answer_collision=answer.clone();answer_collision["operation"]["option"]=json!("8".repeat(32));
 wires.push(hex(&alice.create_message(&a,&ak,&serde_json::to_vec(&answer_collision).unwrap()).unwrap().to_bytes().unwrap()));
 // Prepare and sign real genesis through existing schema helper; no key export.
 let member=alice.members().find(|m|m.signature_key==ak.public()).unwrap();let id=hex(BasicCredential::try_from(member.credential).unwrap().identity());
 let now=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
 let script=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../mls_identity.py");
 let out=std::process::Command::new("python3").arg(script).args(["prepare",&id,&hex(ak.public()),&now.to_string()]).output().unwrap();assert!(out.status.success());
 let strings=String::from_utf8(out.stdout).unwrap();let data:Vec<_>=strings.lines().collect();let mut proofs=Vec::new();
 for(domain,payload)in [("email-next/device-binding/v0",data[0]),("email-next/device-possession/v0",data[0]),("email-next/identity-state/v0",data[1])]{let bytes=unhex(payload).unwrap();let mut input=domain.as_bytes().to_vec();input.push(0);input.extend((bytes.len()as u32).to_be_bytes());input.extend(bytes);proofs.push(hex(&ak.sign(&input).unwrap()));}
 json!({"checkpoint":initial,"group":hex(bob.group_id().as_slice()),"wires":wires,"binding":data[0],"state":data[1],"proofs":proofs,"time":now.to_string()})
}
fn main(){let result=if std::env::args().nth(1).as_deref()==Some("--fixture"){fixture()}else{let mut b=Vec::new();std::io::stdin().take((MAX+1)as u64).read_to_end(&mut b).unwrap();if b.len()>MAX{json!({"status":"worker-rejected"})}else{match serde_json::from_slice(&b).map_err(|_|"json".to_string()).and_then(receive){Ok(v)=>v,Err(reason)=>json!({"status":"worker-rejected","reason":reason})}}};let out=serde_json::to_vec(&result).unwrap();if out.len()>MAX{std::process::exit(2)}std::io::stdout().write_all(&out).unwrap();}
