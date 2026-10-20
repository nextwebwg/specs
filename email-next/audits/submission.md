---
title: Message submission audit
sectionNav: true
---

# Message submission audit

**Coverage:** complete twenty-page [RFC 6409](https://www.rfc-editor.org/rfc/rfc6409.html), including the extension table, appendix, references and end matter. Verified erratum 3995 and its verifier caveat reviewed. Modern submission TLS requirements are covered separately by the RFC 8314/8997 audits; other dependencies remain open.

## Finding

An MSA can complete or modify submitted mail. That permission does not guarantee preservation of endpoint signatures, and it does not give ordinary relays the same authority. Email Next must finish protected contributions before applying protection and distinguish provider-added security from endpoint security.

| Section | Disposition |
| --- | --- |
| 1 | Submission may complete unfinished messages; downstream relays do not inherit general modification authority. Separating submission improves authorization and diagnostics. |
| 2 | Document conventions and architecture terms reviewed. |
| 2.1 | MSA accepts submissions and relays/delivers; MTA transfers; MUA composes and reads. Fully qualified domain is globally resolvable, not a local abbreviation. |
| 2.2 | Example domain and requirement vocabulary reviewed. |
| 3 | Submission behavior is distinct from relay behavior. |
| 3.1 | 587 identifies ESMTP submission; designated25 submission allowed by source. Modern implicit TLS policy reviewed separately under8314/8997. |
| 3.2 | Reject rather than damage mail. Unknown return route to submitter should reject immediately; null MAIL FROM alone must not cause rejection. Other rejections may be delayed bounces, but immediate feedback preferred; client needs submitted-message correlation. |
| 3.3 | SMTP AUTH, network authorization and tunnels discussed; IP trust and POP-before-SMTP have spoofing/window limits. Historical options are not endpoint identity proof. |
| 4 | Mandatory MSA duties apply to submission. |
| 4.1 | 554 is general improper MAIL/RCPT/DATA rejection unless more precise code applies. |
| 4.2 | Envelope domains must be qualified; examining/modifying text beyond trace triggers qualification duty for address headers. Verified local single-label expansion possible; incomplete multi-level expansion discouraged. |
| 4.3 | Default MAIL530 without SMTP authentication unless independent authentication/authorization already established. |
| 5 | Recommended MSA duties reviewed. |
| 5.1 | Illegal envelope/address header syntax should reject; MAIL/RCPT501, post-DATA invalid address554 with suitable detail. |
| 5.2 | Log client errors with limits to prevent logging denial of service. |
| 5.3 | Submission servers should respond in under2minutes evenDATA; tightly coupled systems may agree shorter timeouts. Timeout is not proof of nonacceptance. |
| 6 | Optional actions do not universally require provider rewriting. |
| 6.1 | MAIL sender authorization can be enforced with550 and appropriate detail. |
| 6.2 | RCPT permissions can be enforced separately from sender authorization. |
| 6.3 | Data syntax554, command syntax501, user or site policy550; failure may occur atDATA or after content. |
| 6.4 | Local policy may relax authentication for postmaster to permit reporting submission problems; not general open submission. |
| 6.5 | Charset/string conversion and known out-of-band address substitution allowed subject to other protocols; not arbitrary transliteration or signature preservation guarantee. |
| 7 | Entire extension table reviewed. AUTH mandatory; PIPELINING/enhanced codes/DSN/8BITMIME recommended; ETRN/ATRN/521 prohibited for submission. Other table options conditional. Historical STARTTLS optionality is not the current8314 security baseline. DATA references includeBDAT. |
| 8 | MSA modifications must remedy specific understood problems; forwarded output meets SMTP/message format or negotiated extensions. Modifications may invalidate DKIM/PGP/S/MIME signatures. |
| 8.1 | May add/replace Sender when known and absent fromFrom; inserted address must be valid. |
| 8.2 | May add missingDate or repair syntax, not invent authenticated author chronology. |
| 8.3 | Should add/replace missing or syntactically invalidMessage-ID. Endpoint event identity must not depend solely on mutable outer field. |
| 8.4 | MIME transfer encoding permitted only if needed and not harmful to type; signature-byte coverage remains separate. |
| 8.5 | Provider may sign/add authentication; provider signature is not endpoint authority. |
| 8.6 | Provider encryption may implement organizational policy; protected submission connection needed for usefulness, and provider access is not endpoint confidentiality. |
| 8.7 | Alias rewriting optional. Verified3995 corrects false SMTP alias prohibition; verifier cautions replacement wording needs further care. Follow5321 rules, not blanket DNS canonicalization. |
| 8.8 | Only specific configured address mappings; no data-independent truncation. Destination local-part constraints remain; sufficiently informed substitutions under6.5 allowed. |
| 9 | Authorization prevents resource/name abuse; separate services enable policy distinctions. Logging and authentication weaknesses remain relevant. |
| 10 | Submission applicability registry and587 reference updates; no new Email Next registration made. |
| 11 | Acknowledgements reviewed. |
| 12 | References reviewed, dependency closure remains open. |
| 12.1 | 4954 still needs full audit;5321 already reviewed; requirement vocabulary inherited. |
| 12.2 | Table extensions, DSN/status, crypto successors, access and transport dependencies tracked separately; informative listing is not proof of implementation. |
| Appendix A | Changes from4409 clarify references, extension table, shorter timeouts, encoding conversion and signed-message risks; no substantial new protocol claimed. |

| Front/end matter | Abstract, status, copyright and author addresses reviewed. |

## Protection boundary

The [transport contract](../transport.md) requires an Email Next submission integration to preserve protected contributions or fail visibly. This is the proposed profile's stricter rule, not a claim that RFC 6409 prohibits all modifications. Trace and routing metadata have their own rules. A provider can add its own signature without acquiring authority to recreate an endpoint signature.

Submission acceptance can precede a later failure. Preserve the contribution and transport-attempt identities needed to correlate those results without treating every retry as a new user action. Outer Message-ID completion does not establish endpoint event identity.

Verified erratum 3995 corrects the claim that SMTP generally prohibits domain aliases. Its verifier explicitly cautions that the proposed replacement wording still needs care. Do not use the old note as authority for blanket address rewriting or identity merging.

## Verification boundary

Required cases include unauthenticated submission, independent authorization, null return path, missing versus malformed identifiers, qualified-address handling, signed-content rewriting, outer trace additions, provider signatures, conversion failures, delayed bounces, uncertain acknowledgements and modern secure submission. No real MSA compatibility test is claimed.
