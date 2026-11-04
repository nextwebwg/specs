---
title: Certificate status and OCSP audit
sectionNav: true
---

# Certificate status and OCSP audit

A valid HTTPS certificate and a fresh statement about its revocation status answer different questions. The [service contract](../service-answers.md#select-a-certificate-status-mode) permits an explicit ordinary-Web mode when status is indeterminate, and provides a stricter mode that requires fresh status or a valid exception. Neither treats unknown status as good.

This review covers the rules needed to accept certificate-status responses: which certificate a response describes, who may sign it, how long it remains usable, and when a TLS server must provide it. It does not cover every feature of OCSP or the TLS Feature extension.

## What a response proves

RFC6960 requires the client to bind the response to the requested certificate, validate its signature and responder authority, and check its times. A CA can answer directly; an authorized delegated responder needs the applicable OCSP-signing authorization. A response containing certificates does not make them trusted roots. A good result does not establish that a certificate was issued, is currently valid, matches the service, or authorizes an action. Unknown and unsigned protocol errors do not establish good status. `ocsp-nocheck` concerns the authorized responder's own certificate; it is not an exemption for arbitrary service certificates. [RFC6960 §§2–4](https://www.rfc-editor.org/rfc/rfc6960.html#section-2)

The proposed service profile limits response age to seven days and allows a 300-second future tolerance. Local policy may be stricter. A finite multi-day interval accommodates cached responses while bounding replay; the clock tolerance accommodates modest skew. Neither value comes from a universal RFC requirement. The profile allows no grace after `nextUpdate`, and an unreliable clock prevents ordinary certificate validity checking in both modes. An accepted response can still predate a newly recorded revocation. `producedAt` does not replace `thisUpdate`. [RFC6960 §§3.2 and 4.2.2.1](https://www.rfc-editor.org/rfc/rfc6960.html#section-3.2)

The [RFC9608 exception](no-revocation.md) applies per certificate and includes mandatory rejection of conflicting extensions. A missing status URL is not that exception. The experiment's extension checker does not independently authenticate the certificate.

## Supplied staples must validate

TLS1.3 carries the status response in the corresponding CertificateEntry. Its deprecated `status_request_v2` extension is not an alternative. RFC6066 requires rejection of an unsatisfactory supplied OCSP response; the current TLS specification retains the fatal status-response alert. The service therefore rejects an invalid supplied peer staple in either status mode, rather than converting it into ordinary retrieval unavailability. [RFC9846 §4.5.1.1](https://www.rfc-editor.org/rfc/rfc9846.html#section-4.5.1.1), [RFC6066 §8](https://www.rfc-editor.org/rfc/rfc6066.html#section-8)

The service requests status and enforces the TLS Feature declaration. It selects no exception for obtaining substitute status after a required staple is missing. Required-staple certificates use full handshakes, without session resumption; pooling remains bounded by the original validated expiry. This explicit profile restriction avoids treating successful resumption as newly supplied status evidence. RFC7633's declaration does not prevent an attacker obtaining a different, unmarked certificate from an issuer. [RFC7633 §§4–5](https://www.rfc-editor.org/rfc/rfc7633.html#section-4)

## Nonces and algorithms

RFC9654 replaces the earlier nonce update in RFC8954. Requesters implementing its extension generate at least 32 octets; responders supporting it must accept 16–32 octets and may omit other permitted lengths. The selected 32-octet request is an interoperable profile choice. A matching nonce binds a response to that request. A missing nonce can supply only independently fresh cached evidence; it does not prove a live answer. [RFC9654 §§2–3](https://www.rfc-editor.org/rfc/rfc9654.html#section-2)

Certificate and OCSP signature algorithms are separate from hash functions used to identify a certificate or responder. Rejecting SHA-1 signatures does not imply rejecting the OCSP SHA-1 identifier formats. The service uses a maintained backend's explicitly configured algorithm policy, with the [selected RSA verification rules](rsa-certificate-signatures.md) and separately reached ECDSA key/signature identifiers; local RSA-only certificates do not establish general algorithm compatibility.

## Evidence and limits

The [policy experiment](../evidence/README.md#certificate-status-policy) tests synthetic backend observations, freshness boundaries and real TLS socket gating. It does not acquire or authenticate OCSP, implement a certificate validator, or establish platform compliance. The private native probe separately found that platform positive-response validation alone did not enforce this profile's exact `nextUpdate` boundary. The specification therefore does not equate a platform API success with implementation of the full status contract.

Captured RFC6960 errata include six Verified corrections (6165, 6166, 6167, 7961, 7962, 5891), one Held editorial correction (5730), and one Rejected nonce proposal (5929). The key-identifier corrections exclude the BIT STRING unused-bit-count octet as well as tag and length. Current nonce behavior follows RFC9654. The captured RFC7633 search has Rejected record4571, a terminology proposal that does not amend processing. The captured RFC9654 search reports no matching errata. RFC6960 is updated by RFC8954 and RFC9654; RFC9654 obsoletes RFC8954. Captured RFC7633 metadata lists no update or replacement.

The selected current RFC6960 AppendixB.2 imports map to the common types, algorithm identifiers and explicit/implicit certificate modules described in the [certificate-module review](rsa-certificate-signatures.md#read-the-module-with-its-corrections). Verified5891 adds the missing CRLReason import; it retains its ENUMERATED semantics, not arbitrary INTEGER decoding. This selected import mapping does not authorize the historical algorithms named in the module or substitute RFC5912's older OCSP module. Optional OCSP archive, service-locator and preferred-algorithm negotiation features, transport registrations, public status retrieval, all-platform behavior and deployed revocation availability remain outside this selected review. They are not silently certified by these tests. The original response-policy and errata capture is dated20 October2026; the selected current-module import mapping is a separate source reconciliation, not a full OCSP audit.
