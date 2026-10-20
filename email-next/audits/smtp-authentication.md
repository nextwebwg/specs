---
title: SMTP authentication audit
sectionNav: true
---

# SMTP authentication audit

**Coverage:** complete twenty-page [RFC 4954](https://www.rfc-editor.org/rfc/rfc4954.html), including grammar, examples, change history and end matter. All seven matching errata in the retrieved dataset reviewed: Verified 1, 1021, 1022, 4015 and 5224; Held for Document Update 1019; Rejected 1020.

## Finding

SMTP AUTH establishes a session identity and can protect the next-hop connection. It explicitly does not establish authorship of message content. MAIL FROM AUTH carries a separately trusted origin claim; an unknown origin must not acquire the authenticated relay's identity.

| Section | Disposition |
| --- | --- |
| 1 | Session authentication/security layer and optional message submitter claim are separate. Held1019 editorial articles do not change semantics. |
| 2 | Requirement vocabulary and C/S example notation reviewed. |
| 3 | AUTH EHLO lists mechanisms and may change afterSTARTTLS; AUTH command plus optionalMAIL AUTH parameter, which adds500characters toMAIL limit. Applicable to submission. |
| 4 | Reject AUTH after success or during transaction503. Challenges334 strictbase64, cancellation*501, zero initial= distinct from omission, invalidbase64501/5.5.2. Initial command retains SMTP limit; exchange must support mechanism sizes, bufferoverflow500/5.5.6. SASLprepSHOULD and failed preparation rejection; success235/failure535. Security layer resets prior SMTP knowledge; freshEHLO, TLS wrapsSASL. AUTHlastpipeline except clientfirstsingle-roundno-layer. HistoricalPLAIN/TLSmandatoryimplementation and CRAM-MD5option do not select modern security policy. Verified4015 and5224 correct references. |
| 4.1 | PLAIN with/without initial response, server-firstCRAM-MD5, EXTERNALemptyresponse examples reviewed. Verified1 corrects three greeting lines to220space rather than unterminated220-hyphen. Historical mechanisms not recommended here. |
| 5 | MAIL AUTH xtext identifies claimed original submitter, not authenticated relay. Trusted claim may propagate; unknown/untrusted uses<> and must not inherit relay identity. Accept parameter syntax even without client auth; originalsubmission may derive mailbox; lists may create newsubmission. Verified1021 editorial correction applied. |
| 5.1 | xtext +3D escapes literal equals; AUTH=<> example carries unknown origin, not empty password. |
| 6 | 235success;432transition;454temporaryserverfailure without newpasswordprompt;534mechanismweak;535credentialsinvalid;500exchangeoverflow;530authrequired with listedcommandexceptions.538historical, do not advertise mechanisms unavailable without encryption. Registry updates reviewed separately5248. |
| 7 | Received insertion plus recommendedESMTPA/ESMTPSA describes hop authentication, not endpoint authorship. |
| 8 | ABNF reviewed: case-insensitive tokens but case-sensitivebase64; xtext+HH; decodedAUTH mustmailboxor<>; initial= and cancel*; no forgivingMIMEbase64 parser. |
| 9 | Required protected session cannot fall back on attacker-inducedAUTHfailure/absence. Reset prelayerknowledge; AUTH=<> prevents origin misattribution. Failedattempt policy and protectedPLAINconfiguration; explicitnotreplacementforend-to-endcrypto. Verified1022 fixes§14reference; Rejected1020 notadopted. |
| 10 | smtp SASL service andAUTH extension registration updated; no EmailNextregistration implied. |
| 11 | SASL4422, corrected2222reference, SASLprep4013/Stringprep3454, PLAIN4616,base64 RFC4648,DSN/status,trace3848,PKIX dependencies require separate review; modern SMTP/submission/TLS baselines handled elsewhere. |
| 12 | HistoricalTLS1.1 andPGP/S-MIME references are not modernalgorithmselection; current successors tracked separately. PIPELINING reviewed. |
| 13 | Acknowledgments reviewed. |
| 14 | PLAIN requires validated certificate and hostname match; absence/failure prohibitsauthentication. No insecureDNS/CNAME-derivedreferenceidentity. Originalwildcard/SANrules read with newer7817 and currentserviceidentity dependencies. |
| 15 | All13changeitems reviewed: parameteracceptance,initialresponse,PLAIN/TLS,mechanismlist,538deprecation,prep,errors,grammar,pipelining,trace,overflow andeditorialchanges. |

| Front/end matter | Abstract, status, copyright, editor details, intellectual-property notices and funding acknowledgement reviewed. |

## Corrected examples and references

Verified erratum 1 fixes three single-line greetings to use a space after 220. Verified 1021 adds an article without changing the identity distinction. Verified 1022 and 4015 direct PLAIN-over-TLS requirements to section 14. Verified 5224 directs the initial-response fallback reference to RFC 2222 §5.1, because the cited RFC 4422 has no §5.1. Those dependency texts still require their own review.

Held 1019 is editorial; rejected 1020 is not an adopted replacement. The historical 12,288-octet observation for authentication lines is not a universal contemporary buffer limit. Implementations must support the sizes needed by their selected mechanisms.

## Email Next integration

The [transport contract](../transport.md) preserves session identity, claimed submitter and endpoint author as separate facts. It forbids using login success or a trace label to enroll a key or validate a contribution. Required channel security survives authentication failure, and capability knowledge is refreshed after a negotiated security-layer reset.

Temporary server failure should not make users repeatedly re-enter correct credentials. Mechanism selection remains constrained by configured protection requirements. Historical TLS and name matching in this document do not override the newer mail-service security profile.

## Required verification

Exercise repeated AUTH, AUTH inside a transaction, omitted versus empty initial response, strict base64 and cancellation, long exchanges, layer resets, permitted pipelining, untrusted origin claims, AUTH=<> relay propagation, list expansion, certificate failure, temporary authentication failure and policy-constrained retry. No SASL implementation, credential exchange or real provider test is claimed.
