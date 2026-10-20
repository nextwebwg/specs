---
title: Historical internationalized headers audit
sectionNav: true
---

# Historical internationalized headers audit

The complete base text of [RFC5335](https://www.rfc-editor.org/rfc/rfc5335.html), including grammar, examples, registration form, references and end matter, has been reviewed. This Experimental document is superseded by RFC6532, covered in the [current header audit](internationalized-headers.md). Dependency closure remains separate.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Historical Experimental protocol, superseded by RFC6532; not the current generation baseline. |
| 1.1 | Role of This Specification | Separates non-ASCII bodies, envelope addresses and header fields; transport permission is still required. |
| 1.2 | Relation to Other Standards | Relaxes transfer-encoding prohibition only for message subtypes that explicitly permit it; message/global permits it. |
| 2 | Background and History | UTF8SMTP belongs to the historical experiment; current SMTPUTF8 and retrieval capabilities must be evaluated separately. |
| 3 | Terminology | UTF-8 includes ASCII; terminology and requirement-keyword references reviewed. |
| 4 | Changes on Message Header Fields | Header field names remain ASCII; permitting UTF-8 field bodies does not internationalize all protocol tokens. |
| 4.1 | UTF-8 Syntax and Normalization | UTF-8 grammar excludes invalid scalar encodings; NFC recommendation does not authorize rewriting authenticated received bytes or merging identities. |
| 4.2 | Changes on MIME Headers | Message/global may carry nested transfer encodings after transport transitions; do not apply its permission indiscriminately to message/rfc822. |
| 4.3 | Syntax Extensions to RFC 2822 | Historical syntax retained ASCII message IDs; current RFC6532 supersedes that limitation. Date/time tokens retain their own constraints. |
| 4.4 | Change on addr-spec Syntax | Experimental nested ASCII alternate-address syntax is not current RFC6532 syntax and cannot establish recipient equivalence or authorize fallback. |
| 4.5 | Trace Field Syntax | Trace fields can contain internationalized addresses; verified erratum1509 clarifies header-field terminology, not routing authority. |
| 4.6 | message/global | Message/global preserves internationalized nested messages, but unknown clients may expose an opaque attachment; it is not an invisible-control container. |
| 5 | Security Considerations | Full-length comparisons and octet limits matter; alternate ASCII/non-ASCII addresses may reach different people. Certificate identity must be established, not inferred from pairing. |
| 6 | IANA Considerations | Registration section points to4.4 although the registration form is in4.6; record editorial discrepancy without claiming an approved correction. Current registry audit is separate. |
| 7 | Acknowledgements | Acknowledgments reviewed; no additional protocol behavior. |
| 8 | References | References and full end matter reviewed, including verified author-name correction2322. |
| 8.1 | Normative References | Historical SMTP, message format and EAI references are not adopted in place of their successors; Unicode and ABNF dependencies remain scoped separately. |
| 8.2 | Informative References | Downgrade, POP and IMAP work-in-progress references describe historical experimentation, not current fallback authority. |

## Captured errata

Both captured entries are verified. [Erratum1509](https://www.rfc-editor.org/errata/eid1509) corrects Return-Path terminology to distinguish an individual field from the complete header. [Erratum2322](https://www.rfc-editor.org/errata/eid2322) corrects the editor's name in the first-page heading and footers to A. Yang. Neither reinstates the experimental address-downgrade design in current standards.

## Fallback and identity

An ASCII alternate address is not proof of identity continuity. The historical specification explicitly allows the alternate to reach another mailbox or person. Email Next must not copy capability history, verified key bindings or protected content to that address solely because an old header paired them. Current RFC6531/RFC6532 syntax and recipient policy control new delivery. A display-only historical parser may expose the original address pair as unverified source material without making it a reply or encryption target.
