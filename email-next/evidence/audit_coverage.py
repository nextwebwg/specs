"""Check audit bookkeeping, not whether a substantive review is correct or complete."""
from pathlib import Path
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
index = (ROOT / 'audits/index.md').read_text()
index_rows = re.findall(r'^\| (\d+) \| \[([^\]]+)\]\(([^)]+)\) \|$', index, re.M)
reviewed = [int(n) for n, _, _ in index_rows]
assert len(index_rows) == len(re.findall(r'^\| \d+ \|', index, re.M)), 'Malformed review index row'
for number, title, target in index_rows:
    assert (ROOT / 'audits' / target).is_file(), f'RFC{number}: broken index link {target}'
assert len(reviewed) == len(set(reviewed)), 'Duplicate review index row'
inventory = json.loads((ROOT / 'audits/source-inventory.json').read_text())
ids = [r['rfc'] for r in inventory]
assert len(ids) == len(set(ids)), 'Duplicate source inventory entry'
summary = re.search(r'contains (\d+) RFCs; (\d+) have a recorded complete base-text review', index)
assert summary, 'Missing review index count statement'
assert tuple(map(int, summary.groups())) == (len(ids), len(reviewed)), 'Stale review index counts'
inventory_page = (ROOT / 'audit-inventory.md').read_text()
count = re.search(r'all (\d+) recorded base-document reviews', inventory_page)
assert count and int(count[1]) == len(reviewed), 'Stale inventory review count'
source_count = re.search(r'\*\*(\d+) RFC records\*\*', inventory_page)
assert source_count and int(source_count[1]) == len(ids), 'Stale inventory source count'
for number, _, target in index_rows:
    entry = next(r for r in inventory if r['rfc'] == int(number))
    assert 'full audit and errata pending' not in entry.get('read', '').lower(), f'RFC{number}: indexed complete but base audit status pending'
rows = json.loads((ROOT / 'audits/section-ledger.json').read_text())['sections']
assert set(reviewed) <= set(ids), 'Review not in source inventory'
assert {r['rfc'] for r in rows} <= set(ids), 'Section not in source inventory'
for rfc in reviewed:
    entries = [r for r in rows if r['rfc'] == rfc]
    assert entries, f'RFC{rfc}: no recorded sections'
    duplicates = [k for k,v in Counter(r['section'] for r in entries).items() if v > 1]
    assert not duplicates, f'RFC{rfc}: repeated sections {duplicates}'
    for row in entries:
        assert 'pending individual' not in row['audit'], f'RFC{rfc}: pending section {row["section"]}'
        evidence = row.get('evidence')
        assert evidence, f'RFC{rfc}: section lacks evidence link'
        assert (ROOT / 'audits' / evidence).is_file(), f'RFC{rfc}: missing evidence {evidence}'
print(f'{len(reviewed)} indexed reviews have section dispositions and evidence files; {len(ids)} sources inventoried.')
print('This check does not prove full-text coverage, correct interpretation, errata completeness or dependency closure.')
