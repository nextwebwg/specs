//! Configured comparison fixture. Secret checkpoints must never enter logs.
use openmls::prelude::{tls_codec::*,*};
use openmls_basic_credential::SignatureKeyPair;
use openmls_rust_crypto::OpenMlsRustCrypto;
use serde_json::{json,Value};
use std::io::{Read,Write};
fn hex(b:&[u8])->String{b.iter().map(|x|format!("{x:02x}")).collect()}
fn bytes(v:&Value,k:&str)->Vec<u8>{let s=v[k].as_str().unwrap();assert!(s.len()%2==0&&s.bytes().all(|c|c.is_ascii_digit()||(b'a'..=b'f').contains(&c)));s.as_bytes().chunks_exact(2).map(|c|u8::from_str_radix(std::str::from_utf8(c).unwrap(),16).unwrap()).collect()}
fn checkpoint(p:&OpenMlsRustCrypto)->Value{let map=p.storage().values.read().unwrap();let mut rows:Vec<_>=map.iter().map(|(k,v)|(hex(k),hex(v))).collect();rows.sort();json!(rows)}
fn snapshot(g:&MlsGroup,p:&OpenMlsRustCrypto,key:&SignatureKeyPair)->Value{let exported=g.export_group_info(p.crypto(),key,false).unwrap();let info=match MlsMessageIn::tls_deserialize_exact(&exported.tls_serialize_detached().unwrap()).unwrap().extract(){MlsMessageBodyIn::GroupInfo(i)=>i,_=>panic!()};json!({"group":hex(g.group_id().as_slice()),"epoch":g.epoch().as_u64().to_string(),"predecessor":hex(&info.group_context().tls_serialize_detached().unwrap()),"context":hex(&g.extensions().unknown(0xff00).unwrap().0),"members":g.members().map(|m|json!({"index":m.index.u32(),"identity":hex(BasicCredential::try_from(m.credential).unwrap().identity()),"key":hex(&m.signature_key)})).collect::<Vec<_>>()})}
// Keep the operational predecessor's consumed handshake ratchet independently of
// the retained transition. clear_pending_commit changes only group state; the
// serialized StagedCommit below retains the secrets needed by a later merge.
fn continue_predecessor(g:&mut MlsGroup,p:&OpenMlsRustCrypto,staged:&Value)->Value{
 g.clear_pending_commit(p.storage()).unwrap();
 let continued=checkpoint(p);
 g.merge_staged_commit(p,serde_json::from_value(staged.clone()).unwrap()).unwrap();
 continued
}
fn run(v:Value)->Value{
 let p=OpenMlsRustCrypto::default();{let mut map=p.storage().values.write().unwrap();for row in v["checkpoint"].as_array().unwrap(){assert!(map.insert(bytes(&json!({"v":row[0]}),"v"),bytes(&json!({"v":row[1]}),"v")).is_none());}}
 let op=v["op"].as_str().unwrap();
 if op=="frame"{let m=MlsMessageIn::tls_deserialize_exact(&bytes(&v,"wire")).unwrap();assert_eq!(m.wire_format(),WireFormat::PrivateMessage);let m=m.try_into_protocol_message().unwrap();return json!({"epoch":m.epoch().as_u64().to_string(),"group":hex(m.group_id().as_slice())});}
 let key=SignatureKeyPair::read(p.storage(),&bytes(&v,"key"),SignatureScheme::ED25519).unwrap();
 if op=="join"{let w=match MlsMessageIn::tls_deserialize_exact(&bytes(&v,"welcome")).unwrap().extract(){MlsMessageBodyIn::Welcome(w)=>w,_=>panic!()};let g=StagedWelcome::new_from_welcome(&p,&MlsGroupJoinConfig::builder().wire_format_policy(PURE_CIPHERTEXT_WIRE_FORMAT_POLICY).build(),w,None).unwrap().into_group(&p).unwrap();return json!({"checkpoint":checkpoint(&p),"snapshot":snapshot(&g,&p,&key)});}
 let mut g=if op=="create"{
  let ext=ExtensionType::Unknown(0xff00);let config=MlsGroupCreateConfig::builder().ciphersuite(Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519).wire_format_policy(PURE_CIPHERTEXT_WIRE_FORMAT_POLICY).use_ratchet_tree_extension(true).with_group_context_extensions(Extensions::try_from(vec![Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ext],&[],&[CredentialType::Basic])),Extension::Unknown(0xff00,UnknownExtension(bytes(&v,"context")))]).unwrap()).capabilities(Capabilities::new(None,None,Some(&[ext]),None,Some(&[CredentialType::Basic]))).build();
  MlsGroup::new(&p,&key,&config,CredentialWithKey{credential:BasicCredential::new(bytes(&v,"identity")).into(),signature_key:key.public().into()}).unwrap()
 }else{MlsGroup::load(p.storage(),&GroupId::from_slice(&bytes(&v,"group"))).unwrap().unwrap()};
 let before=snapshot(&g,&p,&key);
 if op=="create"||op=="inspect"{return json!({"checkpoint":checkpoint(&p),"snapshot":before});}
 if op=="merge-local-staged"{
  assert_eq!(v["library"].as_str().unwrap(),"openmls-0.9.1/staged-v0");
  assert_eq!(before["predecessor"],v["predecessor"]);
  let staged:StagedCommit=serde_json::from_value(v["staged"].clone()).unwrap();
  g.merge_staged_commit(&p,staged).unwrap();
  return json!({"before":before,"after":snapshot(&g,&p,&key),"checkpoint":checkpoint(&p)});
 }
 if op=="discard-past"{g.delete_past_epoch_secrets(&p,PastEpochDeletion::delete_all()).unwrap();return json!({"checkpoint":checkpoint(&p),"snapshot":snapshot(&g,&p,&key)});}
 if op=="quorum-context-candidate"{
  let sender=hex(BasicCredential::try_from(g.own_leaf().unwrap().credential().clone()).unwrap().identity());
  let ext=ExtensionType::Unknown(0xff00);
  let extensions=Extensions::try_from(vec![Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ext],&[],&[CredentialType::Basic])),Extension::Unknown(0xff00,UnknownExtension(bytes(&v,"context")))]).unwrap();
  let(commit,welcome,_)=g.update_group_context_extensions(&p,extensions,&key).unwrap();assert!(welcome.is_none());let staged=serde_json::to_value(g.pending_commit().unwrap()).unwrap();let continued=continue_predecessor(&mut g,&p,&staged);
  return json!({"before":before,"after":snapshot(&g,&p,&key),"checkpoint":checkpoint(&p),"localStaged":staged,"continuedCheckpoint":continued,"sender":sender,"wire":hex(&commit.tls_serialize_detached().unwrap()),"welcome":null});
 }
 if op=="remove"{
  let indices=v["indices"].as_array().unwrap().iter().map(|x|LeafNodeIndex::new(u32::try_from(x.as_u64().unwrap()).unwrap())).collect::<Vec<_>>();assert!(!indices.is_empty());
  let sender=hex(BasicCredential::try_from(g.own_leaf().unwrap().credential().clone()).unwrap().identity());
  let(commit,welcome,_)=g.remove_members(&p,&key,&indices).unwrap();assert!(welcome.is_none());let staged=serde_json::to_value(g.pending_commit().unwrap()).unwrap();let continued=continue_predecessor(&mut g,&p,&staged);
  return json!({"before":before,"after":snapshot(&g,&p,&key),"checkpoint":checkpoint(&p),"localStaged":staged,"continuedCheckpoint":continued,"sender":sender,"wire":hex(&commit.tls_serialize_detached().unwrap()),"welcome":null});
 }
 if op=="candidate"||op=="quorum-candidate"||op=="quorum-mixed-candidate"{
  let packages=v["packages"].as_array().unwrap().iter().map(|x|match MlsMessageIn::tls_deserialize_exact(&bytes(&json!({"p":x}),"p")).unwrap().extract(){MlsMessageBodyIn::KeyPackage(k)=>k.validate(p.crypto(),ProtocolVersion::Mls10).unwrap(),_=>panic!()}).collect::<Vec<_>>();
  let mut additions=packages.iter().map(|k|hex(k.hash_ref(p.crypto()).unwrap().as_slice())).collect::<Vec<_>>();additions.sort();
  let (commit,welcome)=if op=="quorum-mixed-candidate"{let indices=v["indices"].as_array().unwrap().iter().map(|x|LeafNodeIndex::new(u32::try_from(x.as_u64().unwrap()).unwrap())).collect::<Vec<_>>();assert!(!indices.is_empty()&&!packages.is_empty());let bundle=g.commit_builder().consume_proposal_store(false).propose_adds(packages.clone()).propose_removals(indices).load_psks(p.storage()).unwrap().build(p.rand(),p.crypto(),&key,|_|true).unwrap().stage_commit(&p).unwrap();(bundle.commit().clone(),bundle.to_welcome_msg())}else if packages.is_empty(){let bundle=g.self_update(&p,&key,LeafNodeParameters::default()).unwrap();(bundle.commit().clone(),bundle.to_welcome_msg())}else{let(c,w,_)=g.add_members(&p,&key,&packages).unwrap();(c,Some(w))};let sender=hex(BasicCredential::try_from(g.own_leaf().unwrap().credential().clone()).unwrap().identity());
  let staged=serde_json::to_value(g.pending_commit().unwrap()).unwrap();let continued=continue_predecessor(&mut g,&p,&staged);let mut result=json!({"before":before,"after":snapshot(&g,&p,&key),"checkpoint":checkpoint(&p),"localStaged":staged,"continuedCheckpoint":continued,"sender":sender,"wire":hex(&commit.tls_serialize_detached().unwrap()),"welcome":welcome.map(|w|hex(&w.tls_serialize_detached().unwrap()))});if op=="quorum-candidate"||op=="quorum-mixed-candidate"{result["additions"]=json!(additions);}return result;
 }
 if op=="receive"||op=="receive-quorum"{
  let m=MlsMessageIn::tls_deserialize_exact(&bytes(&v,"wire")).unwrap();assert_eq!(m.wire_format(),WireFormat::PrivateMessage);
  let processed=g.process_message(&p,m.try_into_protocol_message().unwrap()).unwrap();let empty_aad=processed.aad().is_empty();
  let sender=hex(BasicCredential::try_from(processed.credential().clone()).unwrap().identity());
  let staged=match processed.into_content(){ProcessedMessageContent::StagedCommitMessage(c)=>c,ProcessedMessageContent::OwnPrivateMessage=>panic!(),_=>return json!({"before":before,"after":before,"unmerged":checkpoint(&p),"sender":sender,"unsupported":true})};
  if !empty_aad || !(staged.queued_proposals().all(|q|matches!(q.proposal(),Proposal::Add(_))) || staged.queued_proposals().all(|q|matches!(q.proposal(),Proposal::Remove(_))) || (op=="receive-quorum" && (staged.queued_proposals().all(|q|matches!(q.proposal(),Proposal::GroupContextExtensions(_))) || staged.queued_proposals().all(|q|matches!(q.proposal(),Proposal::Add(_)|Proposal::Remove(_)))))){return json!({"before":before,"after":before,"unmerged":checkpoint(&p),"sender":sender,"unsupported":true});}
  let mut additions=staged.queued_proposals().filter_map(|q|match q.proposal(){Proposal::Add(a)=>Some(hex(a.key_package().hash_ref(p.crypto()).unwrap().as_slice())),_=>None}).collect::<Vec<_>>();additions.sort();
  let removed=staged.self_removed();let terminal_match=if removed&&op=="receive-quorum"&&v["expectedContext"].is_string(){let expected=GroupContext::tls_deserialize_exact(&bytes(&v,"expectedContext")).unwrap();let actual=staged.group_context();actual.protocol_version()==expected.protocol_version()&&actual.ciphersuite()==expected.ciphersuite()&&actual.group_id()==expected.group_id()&&actual.epoch()==expected.epoch()&&actual.tree_hash()==expected.tree_hash()&&actual.extensions().tls_serialize_detached().unwrap()==expected.extensions().tls_serialize_detached().unwrap()}else{false};let context=hex(&staged.group_context().tls_serialize_detached().unwrap());
  let unmerged=checkpoint(&p);g.merge_staged_commit(&p,*staged).unwrap();
  let after=if removed {json!({"group":hex(g.group_id().as_slice()),"epoch":g.epoch().as_u64().to_string(),"predecessor":context,"context":hex(&g.extensions().unknown(0xff00).unwrap().0),"members":g.members().map(|m|json!({"index":m.index.u32(),"identity":hex(BasicCredential::try_from(m.credential).unwrap().identity()),"key":hex(&m.signature_key)})).collect::<Vec<_>>()})}else{snapshot(&g,&p,&key)};
  let mut result=json!({"before":before,"after":after,"checkpoint":checkpoint(&p),"unmerged":unmerged,"sender":sender,"selfRemoved":removed});if op=="receive-quorum"{result["additions"]=json!(additions);result["terminalPublicFieldsMatch"]=json!(terminal_match);}return result;
 }
 panic!()
}
fn main(){std::panic::set_hook(Box::new(|_|{}));let mut b=Vec::new();std::io::stdin().take(16*1024*1024+1).read_to_end(&mut b).unwrap();if b.len()>16*1024*1024{std::process::exit(2)}let value=std::panic::catch_unwind(||run(serde_json::from_slice(&b).unwrap())).unwrap_or_else(|_|json!({"status":"worker-rejected"}));let out=serde_json::to_vec(&value).unwrap();if out.len()>16*1024*1024{std::process::exit(2)}std::io::stdout().write_all(&out).unwrap();}
