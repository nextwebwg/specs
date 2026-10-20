# Language-tag experiment data

These are unmodified official IANA registry snapshots. `manifest.json` records each source URL, File-Date and SHA-256. The experiment verifies the bytes before use and performs no network requests. The snapshots are reproducible experiment inputs, not permanent protocol versions.

To update the experiment, obtain both registries from their recorded official sources, retain the downloaded bytes, update their File-Date and digest in the manifest, and run the focused language-tag tests. Review changed records and expected outcomes before accepting a new dataset. Do not update in response to message content. A deployment update policy remains separate work.

The subtag registry provides typed records and private-use ranges. The extension registry identifies allocated singletons; it does not supply extension-internal data. This experiment does not validate Unicode locale keys, transformed-content semantics, canonicalize tags, judge whether a tag accurately describes text, or alter received HTML labels.

## Redistribution

These two snapshots are IANA protocol registry data, covered by the [IANA/IETF joint licensing statement](https://www.iana.org/help/licensing-terms) and its CC0 1.0 dedication. Both registries are listed in the [protocol registry index](https://www.iana.org/protocols). This applies to the registry data, not linked RFC documents or other website material. The repository records the data separately from the authored experiment code in `REUSE.toml` and includes the CC0 text in `LICENSES/CC0-1.0.txt`.
