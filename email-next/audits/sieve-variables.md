---
title: Sieve variables audit
sectionNav: true
---

# Sieve variables audit

The complete base text of [RFC5229](https://www.rfc-editor.org/rfc/rfc5229.html), including examples, grammar, references and end matter, has been reviewed. The captured full errata corpus contains one entry: verified [erratum5015](https://www.rfc-editor.org/errata/eid5015), correcting an example action from fileinfo to fileinto. This review applies that correction. Dependency closure and current registry verification are separate work. RFC5173's update is covered by the [body-test audit](sieve-body.md).

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Applies only when the script requires variables; requirement declarations themselves are not expanded. |
| 2 | Capability Identifier | The variables capability denotes interpreter support, not recipient support for Email Next. |
| 3 | Interpretation of Strings | Expansion is single-pass, names are case-insensitive, unknown variables become empty; namespace use requires the relevant extension. |
| 3.1 | Quoting and Encoded Characters | Backslash decoding precedes encoded-character decoding and then variable substitution; a backslash does not generally prevent expansion. |
| 3.2 | Match Variables | Successful non-greedy matches populate numbered captures; evaluation short-circuits left-to-right; list iteration order is not fully fixed. Verified erratum5015 corrects fileinfo to fileinto. |
| 4 | Action set | Set requires a constant valid name, cannot assign match variables, is script-local by default and does not cancel implicit keep. |
| 4.1 | Modifiers | Modifiers run by descending precedence; duplicate precedence and unknown modifiers are errors. |
| 4.1.1 | Modifier ":length" | Length counts characters, not UTF-8 octets; do not use it as an SMTP SIZE measurement. |
| 4.1.2 | Modifier ":quotewildcard" | Quotewildcard quotes wildcard syntax only; it is not HTML, JSON, URL or shell escaping. |
| 4.1.3 | Case Modifiers | Case conversion affects ASCII letters only; not Unicode case folding or mailbox canonicalization. |
| 4.1.3.1 | Modifier ":upper" | Upper converts every ASCII lowercase letter. |
| 4.1.3.2 | Modifier ":lower" | Lower converts every ASCII uppercase letter. |
| 4.1.3.3 | Modifier ":upperfirst" | Upperfirst affects only the first character when it is an ASCII lowercase letter. |
| 4.1.3.4 | Modifier ":lowerfirst" | Lowerfirst affects only the first character when it is an ASCII uppercase letter. |
| 5 | Test string | String compares script-supplied lists without implicit whitespace stripping; relational count ignores empty members. |
| 6 | Implementation Limits | Minimum capacities are 128 variables, 32-character names and 4000-character values; runtime overflow must not be an error and should truncate. Unsupported match indexes are syntax errors. |
| 7 | Security Considerations | Sender-controlled captures and truncation make variables unsuitable for security-bearing structures; filtering is not hostile-message authentication. |
| 8 | IANA Considerations | Registers variables as a Sieve capability; no new sender-requested discard behavior. |
| 9 | Acknowledgments | Acknowledgments reviewed; no additional protocol behavior. |
| 10 | References | Both reference lists and end matter reviewed. |
| 10.1 | Normative References | Sieve, relational comparisons, UTF-8, ABNF and requirement-keyword dependencies remain separately scoped. |
| 10.2 | Informative References | Historical Unicode reference, regex draft and spam-test extension do not establish Email Next trust. |

## Consequences for Email Next

Sieve variables can assist recipient-authorized sorting. They cannot establish the authenticity of a capability claim or key. A captured header remains sender-controlled data. Do not store serialized credentials, signed messages or key packages in these variables and then treat the resulting value as the authenticated original: truncation is explicitly allowed at runtime.

Variable assignment does not cancel implicit keep. This extension supplies no universal instruction that makes a legacy client discard a control message. Script execution scope is not durable replay protection. The transport contract therefore requires a separately negotiated authenticated control service before promising special routing; ordinary email remains potentially visible in legacy clients.
