---
title: Archive protection selection
order: 36.1
blurb: pinned file format · independent writer authentication · explicit limits
sectionNav: true
---

# Archive protection selection

The [archive profile](../encrypted-archives.md) selects [C2SP age v1.1.0](https://c2sp.org/age@v1.1.0) for file encryption. This is a scoped dependency review of that selection, not a complete audit of every recipient type or a cryptographic implementation certification.

| Selected source area | Profile disposition |
| --- | --- |
| Conventions and file encoding | Inherited; strict binary representation selected |
| File key, header and payload | Delegated to the age implementation, including completed-file authentication |
| Native X25519 recipient and identity encoding | Selected for one independently retained recovery identity |
| Other recipients and armor | Not enabled by this profile |
| Source testkit | Additional implementation conformance evidence required; the local container tests do not replace it |

The new container's own signing and digest framing belongs to the Email/2 archive contract. The existing [Ed25519](ed25519.md), [SHA-256](sha256.md), [strict JSON](json-encoding.md) and [Unicode](utf8.md) source reviews apply to their respective components. File encryption does not authenticate an archive's originating writer: the profile therefore pins a separate archive-verification key in trusted recovery material.

The local experiment invokes an installed age tool, rejects recipient mixing at its selected boundary and stages all output privately before acceptance. Its tests cover actual encryption/decryption and invalid complete-file authentication. They do not review the tool's implementation, filesystem erasure, operating-system containment, secure credential storage, all source cryptographic dependencies or future quantum security.

The design rejects promoting archive state into live identity or replayable application actions. Historical-author verification and source-content interpretation remain separate from archive-writer verification. Deployment review must preserve that separation rather than turn a valid archive signature into a universal trusted-message badge.
