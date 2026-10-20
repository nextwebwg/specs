"""Offline development evidence only; never a certification or network probe."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import platform
import re
import sys
import subprocess
import unittest

HERE = Path(__file__).resolve().parent


def source_path(name):
    """Manifest paths are local evidence inputs, never arbitrary file reads."""
    if (not isinstance(name, str) or not name or '\\' in name or '\x00' in name or
        name.startswith('/') or any(p in ('', '.', '..') for p in name.split('/')) or
        str(PurePosixPath(name)) != name):
        raise ValueError('Invalid implementation source path')
    resolved = (HERE / name).resolve()
    try:
        resolved.relative_to(HERE.resolve())
    except ValueError:
        raise ValueError('Implementation source escapes evidence directory') from None
    return resolved

def test_status(result):
    if result.errors or result.failures or result.unexpectedSuccesses:
        return 'fail'
    if result.skipped or result.expectedFailures or result.testsRun == 0:
        return 'not-tested'
    return 'pass'


def validate_manifest(manifest):
    if (not isinstance(manifest, dict) or
        manifest.get('format') != 'email-next-acceptance-manifest-0' or
        not isinstance(manifest.get('profile'), str) or not manifest['profile'] or
        not isinstance(manifest.get('cases'), list) or not manifest['cases']):
        raise ValueError('Invalid or empty acceptance manifest')
    sources = manifest.get('sources')
    if (not isinstance(sources, list) or not sources or
        any(not isinstance(name, str) for name in sources) or len(set(sources)) != len(sources)):
        raise ValueError('Invalid implementation source inventory')
    for name in sources:
        source_path(name)
    # Conservatively include quoted local scripts, including subprocess entry
    # points and inline Node imports. This is not a language parser: computed
    # paths and external dependencies still need explicit inventory review.
    for name in sources:
        path = source_path(name)
        if path.suffix in {'.py', '.mjs', '.js'}:
            for reference in re.findall(
                    r"""['"]((?:\./)?[A-Za-z0-9_./-]+\.(?:mjs|js|py))['"]""",
                    path.read_text()):
                dependency_path = (path.parent / reference).resolve()
                if (dependency_path.is_relative_to(HERE.resolve()) and
                        dependency_path.is_file()):
                    dependency = dependency_path.relative_to(HERE.resolve()).as_posix()
                    if dependency not in sources:
                        raise ValueError('Unlisted local script dependency: ' + dependency)
        # Python's import syntax also names modules without filename extensions.
        if path.suffix != '.py':
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            modules = ([node.module] if isinstance(node, ast.ImportFrom) and node.module
                       else [item.name for item in node.names] if isinstance(node, ast.Import)
                       else [])
            for module in modules:
                dependency = module.split('.')[0] + '.py'
                if (HERE / dependency).is_file() and dependency not in sources:
                    raise ValueError('Unlisted local Python dependency: ' + dependency)
    seen = set()
    for case in manifest['cases']:
        if not isinstance(case, dict):
            raise ValueError('Invalid acceptance case')
        for field in ('id', 'requirement', 'description'):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError('Missing case identity or requirement')
        if case['id'] in seen:
            raise ValueError('Duplicate acceptance case identity')
        seen.add(case['id'])
        outcomes = [name for name in ('test', 'unavailable', 'unsupported') if name in case]
        if len(outcomes) != 1:
            raise ValueError('Case must name exactly one test, unavailable reason or unsupported declaration')
        field = outcomes[0]
        if not isinstance(case[field], str) or not case[field].strip():
            raise ValueError('Empty test or unavailable reason')


def evaluate_case(case):
    """A declared unsupported feature is distinct from an unexecuted check.

    Neither status passes a completeness gate. Skips never imply unsupported:
    only an explicit implementation declaration may establish that status.
    """
    item = {key: case[key] for key in ('id', 'requirement', 'description')}
    if 'unsupported' in case:
        item.update(status='unsupported', detail=case['unsupported'],
                    evidence='implementation-declaration')
    elif 'unavailable' in case:
        item.update(status='not-tested', detail=case['unavailable'])
    else:
        stream = io.StringIO()
        suite = unittest.defaultTestLoader.loadTestsFromName(case['test'])
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        item.update(status=test_status(result), test=case['test'], detail=stream.getvalue())
    return item


def run(manifest_name='acceptance-cases.json'):
    raw = source_path(manifest_name).read_bytes()
    manifest = json.loads(raw)
    validate_manifest(manifest)
    sources = {name: hashlib.sha256(source_path(name).read_bytes()).hexdigest()
               for name in manifest['sources']}
    fixture_names = (('button-question.eml', 'button-answer.eml')
                     if manifest_name == 'acceptance-cases.json' else ())
    def fixture_hashes():
        return {name: hashlib.sha256((HERE.parent/'examples'/name).read_bytes()).hexdigest()
                for name in fixture_names}
    fixtures = fixture_hashes()
    results = [evaluate_case(case) for case in manifest['cases']]
    after = {name: hashlib.sha256(source_path(name).read_bytes()).hexdigest()
             for name in manifest['sources']}
    if (after != sources or source_path(manifest_name).read_bytes() != raw
            or fixture_hashes() != fixtures):
        raise ValueError('Acceptance inputs changed during execution; rerun with stable inputs')
    try:
        node = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        node = None
    return dict(format='email-next-acceptance-report-0', profile=manifest['profile'],
                scope='local experiment; no independent client, server or security certification',
                manifestSha256=hashlib.sha256(raw).hexdigest(), python=platform.python_version(),
                fixturesSha256=fixtures, implementationSha256=sources, node=node, cases=results,
                complete=all(case['status'] == 'pass' for case in results))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='acceptance-cases.json',
                        help='manifest path relative to the local evidence directory')
    parser.add_argument('--require-complete', action='store_true',
                        help='also fail when any acceptance scenario has not passed')
    args = parser.parse_args()
    report = run(args.manifest)
    json.dump(report, sys.stdout, indent=2)
    print()
    sys.exit(1 if any(c['status'] == 'fail' for c in report['cases']) or
             (args.require_complete and not report['complete']) else 0)
