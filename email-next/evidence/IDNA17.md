---
title: Unicode17 provider setup
sectionNav: false
---

# Configured Unicode17 domain acceptance

This experimental provider validates canonical ASCII A-label domains using Unicode17 and published IDNA rules. It does not prove mailbox ownership, complete the formal new-character safety review, normalize message text or change mailbox local parts. No draft18 caution set or asymmetric acceptance is applied.

## Setup

Use an ICU78.3 build with Unicode17 data. `configure_idna17.py` takes explicit paths to the ICU common and data libraries and records their hashes plus the vendored idna3.13 source hashes. Paths identify a deployment; the protocol does not require a particular machine or operating system. The current loader expects ICU's version-suffixed78 C symbols; other build conventions require an explicit adapter, not silent fallback.

```
python configure_idna17.py --library /path/to/libicuuc --data-library /path/to/libicudata --output /path/to/idna17-config.json
```

Set `EMAIL_NEXT_IDNA17_CONFIG` to that generated JSON file when running the evidence application. The configured loader checks hashes and actual ICU/Unicode versions. Without configuration, passive discovery retains its A-label pending state and HTTPS reference validation retains its A-label rejection. A configured invalid provider raises a configuration error; it never falls back to the host's Unicode version.

`passive_discovery.mailbox_syntax` and `service_tls.validate_reference_host` use this provider for domains containing A-labels. Their existing ASCII spelling, length and local-part contracts remain in force. Validation decodes each A-label, checks canonical roundtrip and applies the RFC5893 conditions across every label when the domain has a bidi trigger.

## Reproduce verification

Obtain the Unicode17 UCD files named in `ucd17-source-hashes.json` from `https://www.unicode.org/Public/17.0.0/ucd/`, retaining their relative directories. Point `EMAIL_NEXT_UCD17_DIRECTORY` to that directory and `EMAIL_NEXT_IDNA17_RESULTS` to a writable result JSON file. The corpus checker verifies the captured data hashes before checking normalization, full folding, required properties and the derived IDNA table.

```
python check_idna17_corpus.py
python check_idna17_bidi.py
```

Set `EMAIL_NEXT_IDNA17_TEST_CONFIG` to the same deployment JSON for `test_idna17_acceptance.py`; it explicitly skips provider-dependent cases without that setup. The unaffected legacy tests run without the acceptance configuration. Do not mistake skipped cases for configured-provider verification.

The recorded local run passed20034 normalization rows,1112064 scalar folding/property/IDNA comparisons,1112064 bidi-property comparisons, and the affected consumer/signature regressions. The all-scalar comparison rejected idna3.12 atU+A7F1;3.13 is the selected verified package. This evidence does not certify every possible input or every ICU deployment.

## Attribution and limits

Vendored idna3.13 is unmodified BSD3-Clause code; see `vendor_idna17/LICENSE.md` and `PROVENANCE.md`. The isolated loader binds only its private module namespace to ICU. ICU is separately installed and licensed by Unicode; see the distribution's license. Unicode data carry their original notices and [Unicode license](https://www.unicode.org/license.txt). The harness implements the RFC5892 category derivation only to compare the established runtime tables; it is not a new production normalization implementation.

The native adapter converts UTF16 with the host's byte order and verifies that it matches ctypes representation. Local verification ran on little-endian arm64; a big-endian deployment still needs execution evidence. Library hashes are reproducibility pins, not a software-signing or trusted-supply-chain claim. Python's version-independent Punycode codec remains part of the exercised runtime. The new-character review described by RFC8753 remains incomplete for later Unicode releases, independently of algorithmic validation.
