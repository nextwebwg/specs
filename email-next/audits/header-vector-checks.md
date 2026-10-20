---
title: Protected-header vector checks
sectionNav: true
---

# Protected-header vector checks

This is a partial experiment against the baseline examples in [RFC9788 Appendix C](https://www.rfc-editor.org/rfc/rfc9788.html#appendix-C), not a completed header-protection implementation or full RFC audit. The captured RFC text was used as input. Each example's three-space document indentation was removed and line endings were serialized as CRLF; otherwise its displayed content was preserved.

| Example | Result | Scope |
| --- | --- | --- |
| C.1.2, opaque signedData | Signature verification succeeds | Embedded content integrity only; certificate trust was deliberately not evaluated |
| C.1.3, multipart/signed, literal text rendition | Signature verification fails with a digest mismatch | The extracted text has no space after the body signature separator `--` |
| C.1.3, separate modified trial | Signature verification succeeds | The only change restores a trailing ASCII space after that separator |
| C.1.4.1, published decrypted signedData layer | Signature verification succeeds | The outer encrypted envelope was not decrypted by this experiment |
| C.1.6, opaque signedData with multipart body | Signature verification succeeds | Covers the multipart payload, including the image attachment |
| C.1.7, multipart/signed with multipart body, literal text rendition | Signature verification fails | The body signature separator again lacks a trailing space |
| C.1.7, separate modified trial | Signature verification succeeds | Restores only the trailing separator space |
| C.1.8.1, published decrypted signedData with multipart body | Signature verification succeeds | The outer encrypted envelope was not decrypted by this experiment |

The local OpenSSL `smime -verify` operation used `-noverify`, which disables signer certificate-chain verification, not message-signature verification. Success therefore establishes neither trusted sender identity nor certificate-to-address binding. All six baseline signed examples lack header protection by design; signature success does not authenticate their outer Subject or From fields.

The failure is reproducible from the captured text rendition. The successful one-byte modification is evidence that whitespace transcription matters, not permission for a receiver to mutate signed input until a signature passes. No claim is made here about the RFC's XML/HTML rendition or separately hosted vectors, which were not compared in this experiment.

A conformance fixture must retain exact bytes, record any extraction transformation and distinguish original data from a repaired trial. Production verification must use the protocol-defined signed octets, with presentation cleanup performed afterward. The signed-data content from C.1.2 is 303 bytes after unwrapping; the document's shorter diagram count describes body content rather than the entire MIME payload.

The extracted IETF examples remain scratch research inputs. They have not been copied into the distributable evidence suite; any future redistribution must preserve the applicable IETF Trust notices.


## Signed header-protection examples

The six examples C.2.1–C.2.6 were also extracted with the same recorded transformations. The three opaque signedData examples (C.2.1, C.2.3 and C.2.5) verify directly. The three detached examples (C.2.2, C.2.4 and C.2.6) fail as literal text extractions and verify in separate trials restoring the trailing space on the body signature separator. C.2.5 and C.2.6 exercise the older RFC8551HP message/rfc822 wrapping, which is a receive-compatibility case rather than the new composition format.

Two independent mutations of the successful C.2.2 trial test the protection boundary:

| Mutation | Signature result |
| --- | --- |
| Replace only the outer From with an unrelated address | Still valid |
| Replace only the inner protected From with that address | Invalid |

These checks establish the scope of the example's signature, not the trustworthiness of either address. The rendering rule still requires a valid credential-to-address binding before presenting a verified sender. No certificate trust check or actual client rendering was performed. The prose, structures and plaintext of all C.3 examples have now been reviewed; the automated checks below cover their published signed layers.


## Published signed layers of encrypted examples

All 17 published decrypted signedData layers in C.3.1.1–C.3.17.1 pass signature verification using their literal extracted bytes. This uses the layers printed in the RFC; it does not establish that decrypting each outer envelope produces that layer. Certificate trust remains unchecked.

For C.3.1–C.3.16, parsing the verified inner payload also confirms all three of these properties:

- The root Content-Type carries `hp="cipher"`.
- The ordered HP-Outer records match the displayed outer non-structural header fields after header unfolding and field-name case normalization.
- The outer Subject is `[...]` while the authenticated inner Subject retains the message-specific value.

C.3.17 uses the legacy RFC8551HP structure and is excluded from those RFC9788-specific assertions. The comparison is a consistency check of supplied examples, not an implementation of arbitrary hostile-header parsing, confidentiality inference, rendering, or reply composition. In particular, the `hp` value by itself is not proof that an encryption layer was applied.


## Legacy display and attachment consistency

Inspection of the verified payloads for C.3.1–C.3.16 confirms the expected decoration placement: the four simple legacy-display examples mark one text/plain part each; the four complex legacy-display examples mark both text/plain and text/html alternatives. The other eight examples mark neither. Each marked plain-text part contains the required blank-line boundary, and each marked HTML part contains one div with the legacy-display class.

All eight complex payloads contain one decoded PNG attachment, and those PNG bytes have the same SHA-256 digest across the examples. The checks confirm placement and preservation in these supplied examples. They do not demonstrate secure HTML sanitization, correct removal under malformed input, accessibility, or successful rendering in legacy clients. Those require separate implementation tests.


## Worked composition examples: limits and discrepancies

Appendix D.2.2 explicitly states that editing the suggested reply subject defeats the exact-value ReferenceHCP mapping and can expose the original subject. Email Next deliberately strengthens that behavior: confidentiality provenance survives partial editing and is cleared only by the explicit disclosure decision in the delivery policy. This is a proposal choice, not a claim that RFC9788's algorithm already provides that protection.

Appendix D.2.2.1 also shows a legacy display element in a reply using `hcp_no_confidentiality`. Section 5.2.1 step 2 constructs its legacy-display list using only the local HCP before computing the response HCP in step 5. A literal implementation would therefore leave that list empty in this example. The worked payload and the algorithm differ. An implementation should calculate the final exposure decisions before deriving the decorative header list, while preserving the rule that decorations are inside encryption. This reconciliation needs an explicit test and must not be presented as an approved RFC erratum.

Appendices E.1 and E.2 confirm the plain-text and HTML suppression behavior for a single-part payload that itself carries both `hp` and `hp-legacy-display`. Appendix F distinguishes the older RFC8551HP, pEp and deprecated Autocrypt protected-header schemes. Similar MIME shape alone does not establish pEp identity, encryption intent or a trustworthy original exposure record.
