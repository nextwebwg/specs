---
title: TLS server names and HTTP negotiation
sectionNav: true
---

# TLS server names and HTTP negotiation

Sending the intended server name helps a TLS server select a certificate. It does not prove that certificate is valid for the service. Negotiating an application protocol is another separate check: a client that selected HTTP/2 must not send HTTP/1.1 bytes on that connection.

## The service name stays bound to the authorized origin

The configured clients pass the independently authorized DNS host as TLS `server_hostname`. The TLS library sends SNI and verifies the certificate against that host. Certificate-chain and SAN checks remain mandatory even when the server recognizes SNI. The local tests observe the transmitted name and reject a certificate for a different name. [RFC 6066 §3](https://www.rfc-editor.org/rfc/rfc6066.html#section-3)

SNI host names use ASCII, with internationalized names represented as validated A-labels and no trailing dot. IP literals are not permitted in this SNI name type. The experiment's separately documented DNS-only endpoint restriction is narrower than general HTTPS. It does not derive a new service identity from a connection address, redirect or DNS alias. The fixtures use a fixed server certificate rather than a multi-tenant SNI router; deployments that rely on matching TLS and application names must enforce that match. [RFC 6066 §11.1](https://www.rfc-editor.org/rfc/rfc6066.html#section-11.1)

## Check the selected protocol before sending credentials

The direct HTTP clients advertise only `http/1.1`. After the handshake, they inspect the selected protocol before writing a request. A different selected protocol closes the connection. The service, provider and hosted HTTP handlers likewise check selection before dispatch; their server contexts advertise HTTP/1.1. Protocol selection belongs to the connection, not a remembered session setting. [RFC 7301 §3](https://www.rfc-editor.org/rfc/rfc7301.html#section-3)

For these configured HTTPS endpoints, an absent ALPN selection explicitly falls back to HTTP/1.1. Absence is not evidence that negotiation succeeded. This compatibility choice does not authorize a different protocol, weaker TLS, certificate bypass or endpoint change.

The local Python/OpenSSL wrapper has a concrete limitation: configuring protocol lists alone can produce no selection when the two lists have no overlap. RFC 7301 requires an ALPN-aware server to abort that case with `no_application_protocol`. The exposed Python selection interface does not distinguish an absent offer from an unmatched offer. The current fixtures therefore do not establish that server requirement. A deployment claiming complete ALPN handling needs a TLS integration that enforces it; adding a custom ClientHello parser is not part of this experiment.

## Apply TLS 1.3's handshake rules

RFC 7301 describes TLS 1.2-era ServerHello placement and cleartext selection. In the selected TLS 1.3 profile, the server's ALPN response belongs in EncryptedExtensions. The client offer and ordinary SNI must not be described as confidential merely because application data is encrypted. No encrypted ClientHello or resumption policy is introduced by this experiment. [RFC 9846 §4.2](https://www.rfc-editor.org/rfc/rfc9846.html#section-4.2)

## Source scope and updates

RFC 7301's complete base text, including handshake diagrams, registrations, references and end matter, was reviewed. Its listed rejected erratum 5176 does not allocate HTTP/1.0 or HTTP/0.9 identifiers. The selected review of RFC 8447 covers the registry-name change and registration of alert 120; it does not select a new ALPN identifier or complete all TLS registry dependencies. RFC 8447's later update RFC 9847 remains a separate registry-policy dependency if new registrations are proposed. [RFC 8447 §§3 and 13](https://www.rfc-editor.org/rfc/rfc8447.html#section-13)

The selected RFC6066 review covers SNI §§3/11.1 and status_request §§8/11.6, with TLS1.3 status carriage governed by RFC9846 §4.5.1.1. The [status-evidence owner](../service-answers.md#accept-status-evidence) selects an empty responder-ID list and zero extension octets for the request, then independently validates any supplied response. This source mapping does not establish implemented status acquisition or verification. Its verified correction 3283 confirms one name per name type. Verified4817 corrects the ResponderIDs wording; it does not amend the independent OCSP validation requirements. Reported erratum 5658 proposes DNS-SRV guidance and is not adopted as a published rule. TLS 1.3 and current TLS recommendations were reviewed separately; the record-size-limit update is outside this SNI selection. This is not a full review of every RFC 6066 extension. [RFC 6066 errata](https://errata.rfc-editor.org/search/?rfc_number=6066)
