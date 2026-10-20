import copy
import io
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from run_acceptance import test_status, validate_manifest, evaluate_case, source_path, run

class AcceptanceRunnerTests(unittest.TestCase):
    def test_subprocess_script_and_its_import_must_be_fingerprinted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'entry.py').write_text("worker = 'worker.mjs'\n")
            (root/'worker.mjs').write_text("import './helper.mjs';\n")
            (root/'helper.mjs').write_text("export const result = 1;\n")
            manifest = dict(format='email-next-acceptance-manifest-0', profile='test',
                sources=['entry.py'], cases=[dict(id='one', requirement='../adoption.md',
                    description='Case', unavailable='No adapter')])
            with patch('run_acceptance.HERE', root):
                for dependency in ('worker.mjs', 'helper.mjs'):
                    with self.assertRaisesRegex(ValueError, 'Unlisted local script dependency'):
                        validate_manifest(manifest)
                    manifest['sources'].append(dependency)
                validate_manifest(manifest)

    def test_changed_mail_fixture_cannot_be_reported_as_tested(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'evidence'
            root.mkdir()
            examples = root.parent/'examples'
            examples.mkdir()
            for name in ('button-question.eml', 'button-answer.eml'):
                (examples/name).write_bytes(b'original mail')
            (root/'source.py').write_text('# source')
            (root/'acceptance-cases.json').write_text(json.dumps(dict(
                format='email-next-acceptance-manifest-0', profile='test',
                sources=['source.py'], cases=[dict(id='one', requirement='../messages.md',
                    description='Mail fixture', test='example.test')])))
            def change_fixture(case):
                (examples/'button-question.eml').write_bytes(b'different mail')
                return dict(id=case['id'], status='pass')
            with patch('run_acceptance.HERE', root), patch(
                    'run_acceptance.evaluate_case', side_effect=change_fixture):
                with self.assertRaisesRegex(ValueError, 'inputs changed'):
                    run('acceptance-cases.json')

    def test_local_import_cannot_escape_source_fingerprints(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'entry.py').write_text('from helper import result\n')
            (root/'helper.py').write_text('result = 1\n')
            manifest = dict(format='email-next-acceptance-manifest-0', profile='test',
                sources=['entry.py'], cases=[dict(id='one', requirement='../adoption.md',
                    description='Case', unavailable='No adapter')])
            with patch('run_acceptance.HERE', root):
                with self.assertRaisesRegex(ValueError, 'Unlisted local Python dependency'):
                    validate_manifest(manifest)
                manifest['sources'].append('helper.py')
                validate_manifest(manifest)

    def test_changed_inputs_cannot_produce_a_report_for_untested_bytes(self):
        for changed in ('source.py', 'manifest.json'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root/'source.py').write_text('# original')
                (root/'manifest.json').write_text(json.dumps(dict(
                    format='email-next-acceptance-manifest-0', profile='test',
                    sources=['source.py'], cases=[dict(
                        id='one', requirement='../adoption.md', description='A case',
                        test='example.test')])))
                def change_input(case):
                    with (root/changed).open('a') as output:
                        output.write('\n ')
                    return dict(id=case['id'], status='pass')
                with patch('run_acceptance.HERE', root), patch(
                        'run_acceptance.evaluate_case', side_effect=change_input):
                    with self.assertRaisesRegex(ValueError, 'inputs changed'):
                        run('manifest.json')

    def test_unexecuted_and_exceptional_outcomes_cannot_pass(self):
        for expected, mode in [('pass','pass'), ('fail','fail'), ('not-tested','skip'),
                               ('not-tested','expected-fail'), ('fail','unexpected-pass')]:
            def method(self, mode=mode):
                if mode in ('fail','expected-fail'): self.fail('fixture failure')
            if mode=='skip': method=unittest.skip('fixture')(method)
            if mode in ('expected-fail','unexpected-pass'): method=unittest.expectedFailure(method)
            with self.subTest(mode=mode):
                fixture = type('OutcomeFixture', (unittest.TestCase,), {'runTest':method})
                result = unittest.TextTestRunner(stream=io.StringIO()).run(fixture())
                self.assertEqual(test_status(result), expected)
        self.assertEqual(test_status(unittest.TestResult()), 'not-tested')
        suite = unittest.defaultTestLoader.loadTestsFromName('missing_acceptance_fixture_xyz')
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        self.assertEqual(test_status(result), 'fail')

    def test_manifest_cannot_hide_cases_through_duplicates_or_ambiguous_status(self):
        good = dict(format='email-next-acceptance-manifest-0',profile='test',sources=['run_acceptance.py'],cases=[
            dict(id='one',requirement='../messages.md',description='A case',test='example.test')])
        validate_manifest(good)
        for change in ['empty','duplicate','both','neither','blank']:
            value=copy.deepcopy(good)
            if change=='empty': value['cases']=[]
            elif change=='duplicate': value['cases']*=2
            elif change=='both': value['cases'][0]['unavailable']='No adapter'
            elif change=='neither': del value['cases'][0]['test']
            elif change=='blank': value['cases'][0]['requirement']=' '
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_manifest(value)

    def test_source_inventory_cannot_escape_or_duplicate_files(self):
        base=dict(format='email-next-acceptance-manifest-0',profile='test',cases=[
            dict(id='one',requirement='../messages.md',description='A case',unavailable='No adapter')])
        for sources in [[], ['../secret'], ['a/../b'], ['a//b'], ['./a'], ['/tmp/a'],
                        ['a\\b'], ['same.py','same.py'], [None], ['a\x00b']]:
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                validate_manifest(dict(base,sources=sources))

    def test_nested_source_inputs_are_hashed_without_following_escape_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'evidence';root.mkdir()
            (root/'data').mkdir();(root/'data'/'source.json').write_text('{}')
            outside=Path(directory)/'private.txt';outside.write_text('private')
            (root/'escape.txt').symlink_to(outside)
            with patch('run_acceptance.HERE',root):
                self.assertEqual(source_path('data/source.json').read_bytes(), b'{}')
                with self.assertRaises(ValueError):source_path('escape.txt')

    def test_unsupported_is_declared_not_inferred_from_missing_adapter(self):
        base=dict(id='feature', requirement='../adoption.md', description='Feature support')
        unavailable=evaluate_case(dict(base, unavailable='No adapter'))
        unsupported=evaluate_case(dict(base, unsupported='This implementation does not implement service answers'))
        self.assertEqual(unavailable['status'], 'not-tested')
        self.assertEqual(unsupported['status'], 'unsupported')
        self.assertEqual(unsupported['evidence'], 'implementation-declaration')
        self.assertFalse(all(case['status']=='pass' for case in [unsupported]))
        manifest=dict(format='email-next-acceptance-manifest-0', profile='test',
                      sources=['run_acceptance.py'], cases=[dict(base, unsupported='No service answers')])
        validate_manifest(manifest)
        for additional in [{'test':'example.test'}, {'unavailable':'No adapter'}]:
            value=copy.deepcopy(manifest)
            value['cases'][0].update(additional)
            with self.assertRaises(ValueError): validate_manifest(value)
        manifest['cases'][0]['unsupported']=' '
        with self.assertRaises(ValueError): validate_manifest(manifest)


    def test_selected_manifest_and_default_preserve_case_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'evidence';root.mkdir()
            examples=root.parent/'examples';examples.mkdir()
            for name in ['button-question.eml','button-answer.eml']:(examples/name).write_bytes(b'fixture')
            (root/'source.py').write_text('# source')
            for filename,profile in [('acceptance-cases.json','default'),('provider.json','provider')]:
                (root/filename).write_text(json.dumps(dict(format='email-next-acceptance-manifest-0',profile=profile,sources=['source.py'],cases=[dict(id=profile,requirement='../adoption.md',description='Unavailable integration',unavailable='No adapter')])))
            with patch('run_acceptance.HERE',root):
                default=run()
                self.assertEqual(default['profile'],'default')
                self.assertEqual(set(default['fixturesSha256']),{'button-question.eml','button-answer.eml'})
                report=run('provider.json')
                self.assertEqual(report['profile'],'provider')
                self.assertEqual(report['fixturesSha256'],{})
                self.assertEqual(report['cases'][0]['id'],'provider')
                self.assertFalse(report['complete'])
                self.assertEqual(report['cases'][0]['status'],'not-tested')
                outside=root.parent/'private.json';outside.write_text('{}')
                (root/'escaped.json').symlink_to(outside)
                for name in ['../private.json',str(outside),'escaped.json','./provider.json','a/../provider.json']:
                    with self.subTest(name=name),self.assertRaises(ValueError):run(name)
