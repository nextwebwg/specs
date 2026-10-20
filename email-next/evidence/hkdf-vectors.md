---
title: HKDF known-answer checks
sectionNav: true
---

# HKDF known-answer checks

The isolated `hkdf_vectors.py` harness passes all seven RFC5869 Appendix A known-answer cases using the installed `cryptography` library. Each case checks the extraction result through library HMAC, then checks the expected output through both HKDFExpand and the combined HKDF API. These are three checks per published case, not three independent implementations.

The run used Python 3.14.0, cryptography 50.0.2 and its reported backend OpenSSL 4.0.3 (29 September 2026). It is separate library evidence: it does not execute the pinned OpenMLS implementation, establish end-to-end interoperability or certify cryptographic security.

## Reproduce

From the evidence directory, with cryptography installed:

```sh
python -m unittest test_hkdf_vectors
python hkdf_vectors.py --source /path/to/pinned/rfc5869.txt
```

The optional source check requires SHA-256 `7a40eb3835b35fc947eb12a2ed614db079d43b26e50dbc537c31fba16397089c`, extracts the numeric inputs and expected outputs again, checks stated octet lengths and compares every fixture value. Without `--source`, the harness uses the retained fixture and reports that the source was not rechecked. It does not fetch remote content during a test.

`hkdf-rfc5869-vectors.json` preserves explicit empty salt as an empty hex string and omitted salt as JSON null. The library receives `b''` and `None` respectively; the HMAC extraction check applies the RFC's HashLen-zero default for omitted salt. SHA-1 cases are included to reproduce the complete published vector set, not to select SHA-1 for Email Next.

Four focused tests pass, including incorrect expected-output and substituted-source rejection. Separate SHA-256 boundary checks accept output lengths 0, 1, 8,159 and 8,160 and reject 8,161 for both HKDF and HKDFExpand. The 8,160-byte bound applies to one SHA-256 Expand call; it is not an email or application-event size limit. Boundary checks do not independently establish the expected bytes at the maximum length.

## Source and licensing

The numeric fixture is extracted from [RFC5869 Appendix A](https://www.rfc-editor.org/rfc/rfc5869.html#appendix-A), by Hugo Krawczyk and Pasi Eronen. `hkdf-fixture-LICENSE.txt` retains the IETF Trust/document-author copyright notice and Simplified BSD terms for extracted code components. No whole RFC, specification prose or custom cryptographic implementation is included. The Python harness is original project code calling the established library APIs described in the [cryptography HKDF documentation](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#hkdf).
