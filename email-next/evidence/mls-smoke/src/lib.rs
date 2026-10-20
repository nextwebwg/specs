//! Local MLS exchange with explicit unverified first-contact identity integration.
pub mod package_validation;
#[cfg(test)]
mod tests {
    use openmls::prelude::{tls_codec::*, *};
    use openmls_basic_credential::SignatureKeyPair;
    use openmls_traits::signatures::Signer;
    use openmls_rust_crypto::OpenMlsRustCrypto;
    use std::time::{SystemTime, UNIX_EPOCH};
    use std::io::Write;
    use std::process::{Command, Stdio};

    const SUITE: Ciphersuite = Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519;

    fn credential(provider: &OpenMlsRustCrypto, account: u8, device: u8) -> (CredentialWithKey, SignatureKeyPair) {
        // Fixed nonzero identifiers are test fixtures, not production ID generation.
        let mut identity = b"email-next/device/v0\0".to_vec();
        identity.extend_from_slice(&[account; 32]);
        identity.extend_from_slice(&[device; 32]);
        assert_eq!(identity.len(), 85);
        let key = SignatureKeyPair::new(SUITE.signature_algorithm()).unwrap();
        key.store(provider.storage()).unwrap();
        (CredentialWithKey {credential: BasicCredential::new(identity).into(),signature_key: key.public().into()}, key)
    }

    fn mail_roundtrip(bytes: Vec<u8>) -> Vec<u8> {
        let script = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../mls_mime.py");
        let mut child = Command::new(std::env::var("EMAIL_NEXT_PYTHON").unwrap_or_else(|_| "python3".into()))
            .arg(script).stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn().unwrap();
        child.stdin.take().unwrap().write_all(&bytes).unwrap();
        let output = child.wait_with_output().unwrap();
        assert!(output.status.success(), "MIME fixture failed");
        assert_eq!(output.stdout, bytes);
        output.stdout
    }

    // Captured only from an accepted library group, never incoming JSON/headers.
    struct EpochSnapshot {
        group: String, epoch: String, context: String,
        members: Vec<(String, String, String)>,
    }
    fn epoch_snapshot(group: &MlsGroup) -> EpochSnapshot {
        EpochSnapshot { group: hex(group.group_id().as_slice()), epoch: group.epoch().as_u64().to_string(),
            context: hex(&group.extensions().unknown(0xff00).unwrap().0),
            members: group.members().map(|m| (m.index.u32().to_string(),
                hex(BasicCredential::try_from(m.credential).unwrap().identity()), hex(&m.signature_key))).collect() }
    }
    fn processed_context(message: &ProcessedMessage) -> Vec<String> {
        let index = match message.sender() { Sender::Member(index) => index.u32().to_string(), _ => "not-member".into() };
        vec![hex(message.group_id().as_slice()), message.epoch().as_u64().to_string(), index,
            hex(BasicCredential::try_from(message.credential().clone()).unwrap().identity()), hex(message.aad())]
    }
    fn contribution_result(bytes: &[u8], processed: &[String], snapshot: &EpochSnapshot) -> String {
        let script = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../mls_contribution.py");
        let members: Vec<String> = snapshot.members.iter().map(|(index,identity,key)| format!("{index}:{identity}:{key}")).collect();
        let mut child = Command::new(std::env::var("EMAIL_NEXT_PYTHON").unwrap_or_else(|_| "python3".into()))
            .arg(script).args(processed).arg(&snapshot.group).arg(&snapshot.epoch).arg(&snapshot.context).args(members)
            .stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn().unwrap();
        child.stdin.take().unwrap().write_all(bytes).unwrap();
        let output = child.wait_with_output().unwrap();
        assert!(output.status.success(), "Contribution bridge failed: {}", String::from_utf8_lossy(&output.stderr));
        String::from_utf8(output.stdout).unwrap()
    }

    fn hex(bytes: &[u8]) -> String {
        bytes.iter().map(|b| format!("{b:02x}")).collect()
    }

    fn unhex(value: &str) -> Vec<u8> {
        value.as_bytes().chunks_exact(2).map(|chunk| u8::from_str_radix(std::str::from_utf8(chunk).unwrap(), 16).unwrap()).collect()
    }

    fn identity_bridge(args: &[String]) -> String {
        let script = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../mls_identity.py");
        let result = Command::new(std::env::var("EMAIL_NEXT_PYTHON").unwrap_or_else(|_| "python3".into()))
            .arg(script).args(args).output().unwrap();
        assert!(result.status.success(), "Identity bridge failed");
        String::from_utf8(result.stdout).unwrap()
    }

    fn identity_fixture(identity: &[u8], key: &SignatureKeyPair, now: u64) -> Vec<String> {
        let prepared = identity_bridge(&["prepare".into(), hex(identity), hex(key.public()), now.to_string()]);
        let values: Vec<&str> = prepared.lines().collect();
        assert_eq!(values.len(), 2);
        let binding = unhex(values[0]);
        let state = unhex(values[1]);
        let mut args = vec!["check".into(), values[0].into(), values[1].into()];
        for (domain, payload) in [
            (b"email-next/device-binding/v0\0".as_slice(), binding.as_slice()),
            (b"email-next/device-possession/v0\0".as_slice(), binding.as_slice()),
            (b"email-next/identity-state/v0\0".as_slice(), state.as_slice()),
        ] {
            let mut input = domain.to_vec();
            input.extend_from_slice(&(payload.len() as u32).to_be_bytes());
            input.extend_from_slice(payload);
            args.push(hex(&key.sign(&input).unwrap()));
        }
        args.extend([hex(identity), hex(key.public()), now.to_string()]);
        args
    }

    fn protocol(bytes: &[u8]) -> ProtocolMessage {
        MlsMessageIn::tls_deserialize_exact(bytes).unwrap().try_into_protocol_message().unwrap()
    }

    #[test]
    fn serialized_exchange_with_recovery_after_tampered_input() {
        let alice_provider = OpenMlsRustCrypto::default();
        let bob_provider = OpenMlsRustCrypto::default();
        let (alice_credential, alice_key) = credential(&alice_provider, 1, 2);
        let (bob_credential, bob_key) = credential(&bob_provider, 3, 4);
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        // Avoid the library convenience constructor's additional one-hour margin.
        let lifetime = Lifetime::init(now.saturating_sub(60), now + 604740);
        let package = KeyPackage::builder().key_package_lifetime(lifetime)
            .leaf_node_capabilities(Capabilities::builder().extensions(vec![ExtensionType::Unknown(0xff00)]).build())
            .build(SUITE, &bob_provider, &bob_key, bob_credential).unwrap();
        let package_bytes = mail_roundtrip(package.key_package().tls_serialize_detached().unwrap());
        let received_package = KeyPackageIn::tls_deserialize_exact(&package_bytes).unwrap()
            .validate(alice_provider.crypto(), ProtocolVersion::Mls10).unwrap();
        let mut trailing_package = package_bytes.clone();
        trailing_package.push(0);
        assert!(KeyPackageIn::tls_deserialize_exact(&trailing_package).is_err());
        let mut altered_package = package_bytes.clone();
        *altered_package.last_mut().unwrap() ^= 1;
        assert!(KeyPackageIn::tls_deserialize_exact(&altered_package).unwrap()
            .validate(alice_provider.crypto(), ProtocolVersion::Mls10).is_err());
        let config = MlsGroupCreateConfig::builder().ciphersuite(SUITE)
            .with_group_context_extensions(Extensions::try_from(vec![
                Extension::RequiredCapabilities(RequiredCapabilitiesExtension::new(&[ExtensionType::Unknown(0xff00)], &[], &[CredentialType::Basic])),
                Extension::Unknown(0xff00, UnknownExtension(include_bytes!("../fixtures/context.json").to_vec())),
            ]).unwrap())
            .capabilities(Capabilities::new(None, None, Some(&[ExtensionType::Unknown(0xff00)]), None, Some(&[CredentialType::Basic])))
            .build();
        let mut alice = MlsGroup::new(&alice_provider, &alice_key, &config, alice_credential).unwrap();
        let (_, welcome, _) = alice.add_members(&alice_provider, &alice_key, &[received_package]).unwrap();
        alice.merge_pending_commit(&alice_provider).unwrap();
        let welcome_bytes = mail_roundtrip(welcome.tls_serialize_detached().unwrap());
        let mut trailing_welcome = welcome_bytes.clone();
        trailing_welcome.push(0);
        assert!(MlsMessageIn::tls_deserialize_exact(&trailing_welcome).is_err());
        let welcome = match MlsMessageIn::tls_deserialize_exact(&welcome_bytes).unwrap().extract() {
            MlsMessageBodyIn::Welcome(value) => value,
            _ => panic!("expected Welcome"),
        };
        let tree_bytes = mail_roundtrip(alice.export_ratchet_tree().tls_serialize_detached().unwrap());
        let received_tree = RatchetTreeIn::tls_deserialize_exact(&tree_bytes).unwrap();
        let mut trailing_tree = tree_bytes.clone();
        trailing_tree.push(0);
        assert!(RatchetTreeIn::tls_deserialize_exact(&trailing_tree).is_err());
        let mut bob = StagedWelcome::new_from_welcome(&bob_provider, &MlsGroupJoinConfig::default(), welcome,
            Some(received_tree)).unwrap().into_group(&bob_provider).unwrap();
        assert_eq!(alice.epoch_authenticator().as_slice(), bob.epoch_authenticator().as_slice());
        // Verify the actual authenticated receiver leaf key, not a claimed key from mail.
        let alice_member = bob.members().find(|member| {
            BasicCredential::try_from(member.credential.clone()).unwrap().identity()[21] == 1
        }).unwrap();
        let alice_identity = BasicCredential::try_from(alice_member.credential).unwrap();
        let mut identity_args = identity_fixture(alice_identity.identity(), &alice_key, now);
        identity_args[7] = hex(&alice_member.signature_key);
        assert_eq!(identity_bridge(&identity_args), "authorized-first-contact-unverified");
        let mut substituted = identity_args.clone();
        substituted[7] = hex(bob_key.public());
        assert_eq!(identity_bridge(&substituted), "signing-key-mismatch");
        let mut wrong_identity = identity_args.clone();
        wrong_identity[6] = hex(BasicCredential::try_from(bob.members().find(|member| member.signature_key == bob_key.public()).unwrap().credential).unwrap().identity());
        assert_eq!(identity_bridge(&wrong_identity), "credential-mismatch");
        let mut expired = identity_args.clone();
        expired[8] = (now + 3601).to_string();
        assert_eq!(identity_bridge(&expired), "not-current");
        let mut forged = identity_args.clone();
        forged[3] = "00".repeat(64);
        assert_eq!(identity_bridge(&forged), "invalid");

        let plaintext = include_bytes!("../fixtures/message.json");
        let encrypted = mail_roundtrip(alice.create_message(&alice_provider, &alice_key, plaintext).unwrap().to_bytes().unwrap());
        let mut trailing_message = encrypted.clone();
        trailing_message.push(0);
        assert!(MlsMessageIn::tls_deserialize_exact(&trailing_message).is_err());
        assert!(!encrypted.windows(plaintext.len()).any(|part| part == plaintext));
        let mut altered = encrypted.clone();
        *altered.last_mut().unwrap() ^= 1;
        assert!(bob.process_message(&bob_provider, protocol(&altered)).is_err());
        // Observed OpenMLS 0.9.1 behavior: this decryption failure consumes
        // in-memory ratchet state although the storage write is not reached.
        // Record it explicitly; do not claim rejection is mutation-free.
        assert!(bob.process_message(&bob_provider, protocol(&encrypted)).is_err());
        let group_id = bob.group_id().clone();
        bob = MlsGroup::load(bob_provider.storage(), &group_id).unwrap().unwrap();
        let processed = bob.process_message(&bob_provider, protocol(&encrypted)).unwrap();
        let proof = processed_context(&processed);
        let snapshot = epoch_snapshot(&bob);
        match processed.into_content() {
            ProcessedMessageContent::ApplicationMessage(message) => {
                let decoded = message.into_bytes();
                assert_eq!(decoded, plaintext);
                assert_eq!(contribution_result(&decoded, &proof, &snapshot), "projected-context-matched");
            },
            _ => panic!("expected private application message"),
        }
        assert!(bob.process_message(&bob_provider, protocol(&encrypted)).is_err());
        let wrong = include_bytes!("../fixtures/wrong-sender.json");
        let wrong_wire = mail_roundtrip(alice.create_message(&alice_provider, &alice_key, wrong).unwrap().to_bytes().unwrap());
        let wrong_processed = bob.process_message(&bob_provider, protocol(&wrong_wire)).unwrap();
        let proof = processed_context(&wrong_processed);
        match wrong_processed.into_content() {
            ProcessedMessageContent::ApplicationMessage(message) => {
                assert_eq!(contribution_result(&message.into_bytes(), &proof, &snapshot), "sender-mismatch");
            },
            _ => panic!("expected structured message"),
        }
        for (payload, expected) in [
            (include_bytes!("../fixtures/wrong-conversation.json").as_slice(), "conversation-mismatch"),
            (include_bytes!("../fixtures/wrong-audience.json").as_slice(), "audience-mismatch"),
        ] {
            let wire = mail_roundtrip(alice.create_message(&alice_provider, &alice_key, payload).unwrap().to_bytes().unwrap());
            let processed = bob.process_message(&bob_provider, protocol(&wire)).unwrap();
            let proof = processed_context(&processed);
            match processed.into_content() {
                ProcessedMessageContent::ApplicationMessage(message) => assert_eq!(contribution_result(&message.into_bytes(), &proof, &snapshot), expected),
                _ => panic!("expected structured message"),
            }
        }
        // Actual encrypted edit transport does not supply the receiver's history.
        // The bridge must retain pending status rather than inventing its root.
        let correction = include_bytes!("../fixtures/edit.json");
        let correction_wire = mail_roundtrip(alice.create_message(&alice_provider, &alice_key, correction).unwrap().to_bytes().unwrap());
        assert!(!correction_wire.windows(correction.len()).any(|part| part == correction));
        let processed = bob.process_message(&bob_provider, protocol(&correction_wire)).unwrap();
        let proof = processed_context(&processed);
        match processed.into_content() {
            ProcessedMessageContent::ApplicationMessage(message) => {
                let decoded = message.into_bytes();
                assert_eq!(decoded, correction);
                assert_eq!(contribution_result(&decoded, &proof, &snapshot), "pending");
            },
            _ => panic!("expected encrypted correction"),
        }
        alice.set_aad(b"unsupported-context".to_vec());
        let aad_wire = alice.create_message(&alice_provider, &alice_key, plaintext).unwrap().to_bytes().unwrap();
        alice.set_aad(vec![]);
        let aad_message = bob.process_message(&bob_provider, protocol(&aad_wire)).unwrap();
        let proof = processed_context(&aad_message);
        match aad_message.into_content() {
            ProcessedMessageContent::ApplicationMessage(message) => assert_eq!(contribution_result(&message.into_bytes(), &proof, &snapshot), "unsupported-aad"),
            _ => panic!("expected application content"),
        }
        let reply = mail_roundtrip(bob.create_message(&bob_provider, &bob_key, b"received").unwrap().to_bytes().unwrap());
        match alice.process_message(&alice_provider, protocol(&reply)).unwrap().into_content() {
            ProcessedMessageContent::ApplicationMessage(message) => assert_eq!(message.into_bytes(), b"received"),
            _ => panic!("expected reply"),
        }
        // A delayed old-epoch message remains decryptable: removal is not recall.
        let delayed = mail_roundtrip(alice.create_message(&alice_provider, &alice_key, plaintext).unwrap().to_bytes().unwrap());
        let removed = alice.members().find(|member| member.signature_key == bob_key.public()).unwrap().index;
        let previous_epoch = alice.epoch();
        let (commit, welcome, _) = alice.remove_members(&alice_provider, &alice_key, &[removed]).unwrap();
        assert!(welcome.is_none());
        let commit_wire = mail_roundtrip(commit.to_bytes().unwrap());
        // This fixture has one designated author and no competing commit; it is not an ordering service.
        alice.merge_pending_commit(&alice_provider).unwrap();
        assert_ne!(alice.epoch(), previous_epoch);
        assert_eq!(alice.members().count(), 1);
        assert!(bob.is_active()); // Bob has not received the removal yet.
        let delayed_message = bob.process_message(&bob_provider, protocol(&delayed)).unwrap();
        let proof = processed_context(&delayed_message);
        match delayed_message.into_content() {
            ProcessedMessageContent::ApplicationMessage(message) => {
                let bytes = message.into_bytes();
                assert_eq!(contribution_result(&bytes, &proof, &snapshot), "projected-context-matched");
                assert_eq!(contribution_result(&bytes, &proof, &epoch_snapshot(&alice)), "epoch-context-mismatch");
            },
            _ => panic!("expected delayed old-epoch message"),
        }
        let future = mail_roundtrip(alice.create_message(&alice_provider, &alice_key, b"after removal").unwrap().to_bytes().unwrap());
        assert!(bob.process_message(&bob_provider, protocol(&future)).is_err());
        let removal = bob.process_message(&bob_provider, protocol(&commit_wire)).unwrap();
        match removal.into_content() {
            ProcessedMessageContent::StagedCommitMessage(commit) => {
                assert!(commit.remove_proposals().any(|p| p.remove_proposal().removed() == bob.own_leaf_index()));
                bob.merge_staged_commit(&bob_provider, *commit).unwrap();
            },
            _ => panic!("expected removal commit"),
        }
        assert!(!bob.is_active());
        assert!(bob.create_message(&bob_provider, &bob_key, b"removed sender").is_err());
    }
}
