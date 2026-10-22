//! Configured feasibility worker, not an Email/2 carrier or admission endpoint.
//! The cache-public operation installs a test's already authenticated public
//! proposal solely to give a synthetic attacker every public dependency. It
//! must never be wired to incoming mail or production checkpoint restoration.
use openmls::prelude::{tls_codec::*, *};
use openmls_basic_credential::SignatureKeyPair;
use openmls_rust_crypto::OpenMlsRustCrypto;
use serde_json::{json, Value};
use std::io::{Read, Write};
const MAX: usize = 16 * 1024 * 1024;
fn hex(raw: &[u8]) -> String { raw.iter().map(|v| format!("{v:02x}")).collect() }
fn bytes(value: &Value) -> Result<Vec<u8>, &'static str> {
    let raw = value.as_str().ok_or("hex")?;
    if raw.len() % 2 != 0 || !raw.bytes().all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c)) { return Err("hex"); }
    raw.as_bytes().chunks_exact(2).map(|c| u8::from_str_radix(std::str::from_utf8(c).unwrap(), 16).map_err(|_| "hex")).collect()
}
fn checkpoint(provider: &OpenMlsRustCrypto) -> Value {
    let map = provider.storage().values.read().unwrap();
    let mut entries: Vec<_> = map.iter().map(|(k,v)| (hex(k),hex(v))).collect();
    entries.sort(); json!(entries)
}
fn run(value: Value) -> Result<Value, &'static str> {
    let provider = OpenMlsRustCrypto::default();
    {
        let mut map = provider.storage().values.write().unwrap();
        for row in value["checkpoint"].as_array().ok_or("checkpoint")? {
            if row.as_array().ok_or("checkpoint entry")?.len() != 2 || map.insert(bytes(&row[0])?, bytes(&row[1])?).is_some() { return Err("checkpoint entry"); }
        }
    }
    let mut group = MlsGroup::load(provider.storage(), &GroupId::from_slice(&bytes(&value["group"])?)).map_err(|_| "load")?.ok_or("group")?;
    let key = SignatureKeyPair::read(provider.storage(), &bytes(&value["key"])?, SignatureScheme::ED25519).ok_or("key")?;
    if group.own_leaf().ok_or("own leaf")?.signature_key().as_slice() != key.public() { return Err("own key"); }
    let op = value["op"].as_str().ok_or("op")?;
    if op == "propose-update" {
        let (wire, _) = group.propose_self_update(&provider, &key, LeafNodeParameters::default()).map_err(|_| "proposal")?;
        return Ok(json!({"checkpoint":checkpoint(&provider),"wire":hex(&wire.tls_serialize_detached().map_err(|_| "serialize")?)}));
    }
    if op == "cache-public" {
        // Trusted experiment input, never a cryptographic acceptance operation.
        let proposal = serde_json::from_value(value["publicProposal"].clone()).map_err(|_| "public proposal")?;
        group.store_pending_proposal(provider.storage(), proposal).map_err(|_| "store proposal")?;
        return Ok(json!({"checkpoint":checkpoint(&provider),"pending":group.has_pending_proposals()}));
    }
    if op != "commit-update" && op != "receive-update" { return Err("op"); }
    let message = MlsMessageIn::tls_deserialize_exact(&bytes(&value["wire"])?).map_err(|_| "message")?;
    if message.wire_format() != WireFormat::PrivateMessage { return Err("not private"); }
    let processed = group.process_message(&provider, message.try_into_protocol_message().map_err(|_| "protocol")?).map_err(|_| "commit-crypto-rejected")?;
    if !processed.aad().is_empty() { return Err("aad"); }
    let sender = hex(BasicCredential::try_from(processed.credential().clone()).map_err(|_| "credential")?.identity());
    match (op, processed.into_content()) {
        ("commit-update", ProcessedMessageContent::ProposalMessage(proposal)) => {
            if !matches!(proposal.proposal(), Proposal::Update(_)) { return Err("not update"); }
            let public = serde_json::to_value(&proposal).map_err(|_| "public serialization")?;
            group.store_pending_proposal(provider.storage(), *proposal).map_err(|_| "store proposal")?;
            let (wire, welcome, _) = group.commit_to_pending_proposals(&provider, &key).map_err(|_| "commit")?;
            if welcome.is_some() || group.pending_commit().ok_or("pending commit")?.queued_proposals().count() != 1 { return Err("scope"); }
            group.merge_pending_commit(&provider).map_err(|_| "merge")?;
            Ok(json!({"checkpoint":checkpoint(&provider),"wire":hex(&wire.tls_serialize_detached().map_err(|_| "serialize")?),"publicProposal":public,"proposalSender":sender,"epoch":group.epoch().as_u64().to_string()}))
        }
        ("receive-update", ProcessedMessageContent::StagedCommitMessage(commit)) => {
            if commit.self_removed() || commit.queued_proposals().count() != 1 || !commit.queued_proposals().all(|p| matches!(p.proposal(), Proposal::Update(_))) { return Err("scope"); }
            group.merge_staged_commit(&provider, *commit).map_err(|_| "merge")?;
            Ok(json!({"checkpoint":checkpoint(&provider),"epoch":group.epoch().as_u64().to_string()}))
        }
        _ => Err("content"),
    }
}
fn main() {
    let mut input = Vec::new();
    std::io::stdin().take((MAX + 1) as u64).read_to_end(&mut input).unwrap();
    let result = if input.len() > MAX { Err("input bound") } else { serde_json::from_slice(&input).map_err(|_| "json").and_then(run) };
    let result = match result { Ok(value) => value, Err(reason) => json!({"status":"worker-rejected","reason":reason}) };
    let output = serde_json::to_vec(&result).unwrap();
    if output.len() > MAX { std::process::exit(2); }
    std::io::stdout().write_all(&output).unwrap();
}
