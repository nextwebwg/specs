//! Local secret maintenance. Returned checkpoints contain secrets; never log them.
use openmls::prelude::{tls_codec::*,*};
use openmls_rust_crypto::OpenMlsRustCrypto;
use serde_json::{json,Value};
use std::io::{Read,Write};
use std::time::{UNIX_EPOCH,Duration};
fn hex(b:&[u8])->String{b.iter().map(|x|format!("{x:02x}")).collect()}
fn bytes(v:&Value)->Vec<u8>{let s=v.as_str().unwrap();assert!(s.len()%2==0&&s.bytes().all(|c|c.is_ascii_digit()||(b'a'..=b'f').contains(&c)));s.as_bytes().chunks_exact(2).map(|c|u8::from_str_radix(std::str::from_utf8(c).unwrap(),16).unwrap()).collect()}
fn checkpoint(p:&OpenMlsRustCrypto)->Value{let map=p.storage().values.read().unwrap();let mut rows:Vec<_>=map.iter().map(|(k,v)|(hex(k),hex(v))).collect();rows.sort();json!(rows)}
fn run(v:Value)->Value{
 let p=OpenMlsRustCrypto::default();{let mut map=p.storage().values.write().unwrap();for row in v["checkpoint"].as_array().unwrap(){assert!(map.insert(bytes(&row[0]),bytes(&row[1])).is_none());}}
 let mut group=MlsGroup::load(p.storage(),&GroupId::from_slice(&bytes(&v["group"]))).unwrap().unwrap();
 let snapshot=json!({"group":hex(group.group_id().as_slice()),"epoch":group.epoch().as_u64().to_string(),"predecessor":hex(&group.public_group().group_context().tls_serialize_detached().unwrap()),"context":hex(&group.extensions().unknown(0xff00).unwrap().0),"members":group.members().map(|m|format!("{}:{}:{}",m.index.u32(),hex(BasicCredential::try_from(m.credential).unwrap().identity()),hex(&m.signature_key))).collect::<Vec<_>>()});
 let policy=&v["policy"];let count=usize::try_from(policy["maxPastEpochs"].as_u64().unwrap()).unwrap();
 let tolerance=u32::try_from(policy["outOfOrderTolerance"].as_u64().unwrap()).unwrap();
 let forward=u32::try_from(policy["maximumForwardDistance"].as_u64().unwrap()).unwrap();
 // Pinned OpenMLS serde representation is local storage, not a wire format.
 // Preserve every existing setting except the two explicitly selected policies.
 let mut config=serde_json::to_value(group.configuration()).unwrap();
 config["past_epoch_deletion_policy"]=json!(count);
 config["sender_ratchet_configuration"]=serde_json::to_value(SenderRatchetConfiguration::new(tolerance,forward)).unwrap();
 group.set_configuration(p.storage(),&serde_json::from_value::<MlsGroupJoinConfig>(config).unwrap()).unwrap();
 group.delete_past_epoch_secrets(&p,PastEpochDeletion::delete_all_without_timestamps()).unwrap();
 let cutoff=UNIX_EPOCH.checked_add(Duration::from_secs(v["cutoff"].as_u64().unwrap())).unwrap();
 group.delete_past_epoch_secrets(&p,PastEpochDeletion::before_timestamp(cutoff).max_past_epochs(count)).unwrap();
 let maximum=usize::try_from(policy["maxCheckpointBytes"].as_u64().unwrap()).unwrap();
 let mut cp=checkpoint(&p);let mut dropped=false;
 if serde_json::to_vec(&cp).unwrap().len()>maximum{
  group.delete_past_epoch_secrets(&p,PastEpochDeletion::delete_all()).unwrap();cp=checkpoint(&p);dropped=true;
 }
 let retired=serde_json::to_vec(&cp).unwrap().len()>maximum;
 if retired{group.delete(p.storage()).unwrap();cp=checkpoint(&p);}
 json!({"status":if retired{"retired"}else{"maintained"},"checkpoint":cp,"droppedAllPast":dropped,"snapshot":snapshot})
}
fn main(){std::panic::set_hook(Box::new(|_|{}));let mut raw=Vec::new();std::io::stdin().take(16*1024*1024+1).read_to_end(&mut raw).unwrap();if raw.len()>16*1024*1024{std::process::exit(2)}let result=std::panic::catch_unwind(||run(serde_json::from_slice(&raw).unwrap())).unwrap_or_else(|_|json!({"status":"worker-rejected"}));let out=serde_json::to_vec(&result).unwrap();if out.len()>16*1024*1024{std::process::exit(2)}std::io::stdout().write_all(&out).unwrap();}
