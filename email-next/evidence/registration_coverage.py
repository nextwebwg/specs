"""Inventory guard for literal vendor media types and custom discovery suffixes.

Checks source/document name coverage only, not IANA status, contact appointment,
standards eligibility, complete registration correctness or implementation support.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
INVENTORY=ROOT/'registration-inventory.md'


def check():
    text=INVENTORY.read_text()
    declared=set(re.findall(r'\| `(application/vnd\.[^`]+)` \|',text))
    suffixes=set(re.findall(r'\| `(email2-[a-z]+)` \|',text))
    found=set();locations={};found_suffixes=set()
    for path in ROOT.rglob('*'):
        if (not path.is_file() or path.suffix not in ('.md','.py','.mjs','.js','.rs') or
                path in (INVENTORY,Path(__file__).resolve()) or
                any(part in ('target','node_modules','__pycache__','.venv','vendor_idna17') for part in path.parts)):
            continue
        raw=path.read_text()
        for name in re.findall(r'application/vnd\.[a-z0-9.+-]+',raw,re.I):
            name=name.lower()
            if name=='application/vnd.example+json' and path.name=='attachment-metadata.test.mjs':continue
            found.add(name);locations.setdefault(name,[]).append(str(path.relative_to(ROOT)))
        found_suffixes.update(re.findall(r'\.well-known/(email2-[a-z]+)',raw))
    if found!=declared or found_suffixes!=suffixes:
        raise ValueError(dict(undocumented_media=sorted(found-declared),unbacked_media=sorted(declared-found),
                              undocumented_suffixes=sorted(found_suffixes-suffixes),unbacked_suffixes=sorted(suffixes-found_suffixes)))
    return dict(vendor_media_names=len(found),custom_well_known_names=len(suffixes),
                scope='literal-name-coverage-only')


if __name__=='__main__':print(check())
