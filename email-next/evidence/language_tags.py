"""Offline RFC5646 authoring experiment; no canonicalization or extension semantics.

The checked-in registry versions are experiment inputs, not permanent protocol pins.
Do not use this authoring check to discard received HTML language labels.
"""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

DATA = Path(__file__).with_name("language-data")


@dataclass(frozen=True)
class Validation:
    valid: bool
    reason: str
    extension_contents_checked: bool = False
    canonicalization_performed: bool = False


def _records(text):
    """Read repeated fields, folded values and LF/CRLF registry records."""
    record = {}
    field = None
    for line in text.splitlines() + ["%%"]:
        if line == "%%":
            if record:
                yield record
            record, field = {}, None
        elif line.startswith(" "):
            if field is None:
                raise ValueError("Registry continuation without a field")
            record[field][-1] += " " + line.strip()
        elif line:
            field, separator, value = line.partition(":")
            if not separator:
                raise ValueError("Registry field lacks colon")
            field = field.strip()
            record.setdefault(field, []).append(value.strip())


@lru_cache(maxsize=1)
def _registry():
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    loaded = {}
    for entry in manifest["datasets"]:
        content = (DATA / entry["file"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError("Language registry digest mismatch")
        records = list(_records(content.decode("utf-8")))
        if records[0].get("File-Date") != [entry["file_date"]]:
            raise ValueError("Language registry File-Date mismatch")
        loaded[entry["kind"]] = records[1:]
    subtags, ranges, grandfathered = {}, {}, set()
    for record in loaded["subtags"]:
        kind = record["Type"][0]
        if kind == "grandfathered":
            grandfathered.add(record["Tag"][0].lower())
        elif "Subtag" in record:
            value = record["Subtag"][0].lower()
            if ".." in value:
                low, high = value.split("..")
                ranges.setdefault(kind, []).append((low, high))
            else:
                subtags.setdefault(kind, {})[value] = record
    extensions = {r["Identifier"][0].lower() for r in loaded["extensions"]}
    return subtags, ranges, grandfathered, extensions


def registry_versions():
    """Return reproducibility metadata; does not contact the network."""
    _registry()  # Verify the files before reporting them as the active dataset.
    return json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))


def validate_language_tag(value):
    """Check base RFC5646 validity, including allocated extension identifiers.

    Extension bodies receive grammar checks only. A successful result is not
    extension-specific validity, canonical form, or a claim about actual content.
    Empty strings are not language tags; validate_lang_attribute handles HTML's
    explicit unknown-language value separately.
    """
    if not isinstance(value, str) or not value or not re.fullmatch(r"[A-Za-z0-9-]+", value):
        return Validation(False, "Expected a nonempty ASCII language tag")
    parts = value.lower().split("-")
    if any(not p or len(p) > 8 for p in parts):
        return Validation(False, "Empty or oversized subtag")
    subtags, ranges, grandfathered, extensions = _registry()
    if value.lower() in grandfathered:
        return Validation(True, "Registered grandfathered tag")
    if parts[0] == "x":
        return Validation(len(parts) > 1, "Private use" if len(parts) > 1 else "Private use requires a value")

    def known(kind, subtag):
        return subtag in subtags.get(kind, {}) or any(
            len(subtag) == len(low) and low <= subtag <= high
            for low, high in ranges.get(kind, [])
        )

    language = parts[0]
    if not language.isalpha() or not 2 <= len(language) <= 8 or not known("language", language):
        return Validation(False, "Unregistered or malformed primary language")
    i = 1
    if len(language) <= 3:
        extlangs = []
        while i < len(parts) and len(parts[i]) == 3 and parts[i].isalpha():
            extlangs.append(parts[i])
            i += 1
        if len(extlangs) > 1:
            return Validation(False, "Only one extended-language subtag is permitted")
        if extlangs:
            extlang = subtags.get("extlang", {}).get(extlangs[0])
            if extlang is None or language not in [p.lower() for p in extlang.get("Prefix", [])]:
                return Validation(False, "Unregistered extlang or incorrect extlang prefix")
    if i < len(parts) and len(parts[i]) == 4 and parts[i].isalpha():
        if not known("script", parts[i]):
            return Validation(False, "Unregistered script")
        i += 1
    if i < len(parts) and ((len(parts[i]) == 2 and parts[i].isalpha()) or (len(parts[i]) == 3 and parts[i].isdigit())):
        if not known("region", parts[i]):
            return Validation(False, "Unregistered region")
        i += 1
    variants = set()
    while i < len(parts) and (5 <= len(parts[i]) <= 8 or (len(parts[i]) == 4 and parts[i][0].isdigit())):
        variant = parts[i]
        if variant in variants or not known("variant", variant):
            return Validation(False, "Duplicate or unregistered variant")
        variants.add(variant)
        i += 1
    seen = set()
    while i < len(parts) and len(parts[i]) == 1 and parts[i] != "x":
        singleton = parts[i]
        if singleton in seen or singleton not in extensions:
            return Validation(False, "Duplicate or unallocated extension singleton")
        seen.add(singleton)
        i += 1
        start = i
        while i < len(parts) and len(parts[i]) >= 2:
            i += 1
        if i == start:
            return Validation(False, "Extension requires a value")
    if i < len(parts) and parts[i] == "x":
        if i + 1 == len(parts):
            return Validation(False, "Private use requires a value")
        i = len(parts)  # Every following ASCII alphanumeric subtag is opaque.
    if i != len(parts):
        return Validation(False, "Unexpected subtag or subtag order")
    return Validation(True, "Base tag valid; extension contents are not semantically checked")


def validate_lang_attribute(value):
    """Authoring rule: valid tag or HTML's empty unknown-language value."""
    if value == "":
        return Validation(True, "Explicit unknown language (empty HTML lang)")
    return validate_language_tag(value)
