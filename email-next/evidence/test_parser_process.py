import json,os,subprocess,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from html_tree import project_tree,_project_tree_local
from parser_process import ParserLimits,ParserFailure,run_parser
HERE=Path(__file__).parent
class ParserIsolation(unittest.TestCase):
    def project(self,source,**kwargs):return project_tree(source,mime_charset='utf-8',max_bytes=200000,max_nodes=100,max_depth=32,**kwargs)
    def test_valid_semantics_match_existing_parser(self):
        source=b'<!doctype html><html><head><meta charset="utf-8"></head><body><table><tr><td>A</td></tr></table><p dir="rtl">B &amp; C</p></body></html>'
        expected=_project_tree_local(source,mime_charset='utf-8',max_bytes=200000,max_nodes=100,max_depth=32)
        self.assertEqual(self.project(source),json.loads(json.dumps(expected)))
    def test_deep_and_wide_hostile_input_fail_without_partial_tree(self):
        for source in (b'<div>'*3000+b'x'+b'</div>'*3000,b'<p>x</p>'*10000):
            with self.subTest(size=len(source)),self.assertRaises(ValueError):self.project(source)
    def test_real_wall_and_output_limits(self):
        with self.assertRaisesRegex(ParserFailure,'timeout'):run_parser([sys.executable,'-c','import time;time.sleep(5)'],b'',ParserLimits(wall_seconds=.1))
        with self.assertRaises(ParserFailure):self.project(b'<p>'+b'x'*10000+b'</p>',process_limits=ParserLimits(max_output=128))
    def test_resident_watchdog_is_distinct_from_hard_memory(self):
        with self.assertRaisesRegex(ParserFailure,'resident-watchdog'):
            run_parser([sys.executable,'-c','import time;x=bytearray(100*1024*1024);time.sleep(3)'],b'',ParserLimits(max_resident=48*1024*1024))
    def test_timeout_closes_partly_written_input_and_reaps_worker(self):
        original=subprocess.Popen
        workers=[]
        def track(*args,**kwargs):
            process=original(*args,**kwargs)
            if kwargs.get('stdin')==subprocess.PIPE:workers.append(process)
            return process
        with patch('parser_process.subprocess.Popen',side_effect=track):
            with self.assertRaisesRegex(ParserFailure,'parser-timeout'):
                run_parser([sys.executable,'-c','import time;time.sleep(5)'],
                           b'x'*1048576,ParserLimits(wall_seconds=.05))
        self.assertEqual(len(workers),1)
        self.assertTrue(workers[0].stdin.closed)
        self.assertIsNotNone(workers[0].returncode)
    def test_missing_resident_monitor_fails_closed(self):
        with patch('parser_process.subprocess.run',side_effect=FileNotFoundError('ps unavailable')):
            with self.assertRaisesRegex(ParserFailure,'resident-monitor-unavailable'):
                run_parser([sys.executable,'-c','import time;time.sleep(5)'],b'',ParserLimits())
    def test_cpu_limit_and_descendant_timeout_cleanup(self):
        command='import sys;sys.path.insert(0,'+repr(str(HERE))+');from parser_process import *;install_worker_limits(ParserLimits(cpu_seconds=1));exec("while True: pass")'
        with self.assertRaises(ParserFailure):run_parser([sys.executable,'-c',command],b'',ParserLimits(wall_seconds=4,cpu_seconds=1))
        with tempfile.TemporaryDirectory() as directory:
            pidfile=Path(directory)/'pid'
            command='import subprocess,time;from pathlib import Path;p=subprocess.Popen(['+repr(sys.executable)+',"-c","import time;time.sleep(20)"]);Path('+repr(str(pidfile))+').write_text(str(p.pid));time.sleep(20)'
            with self.assertRaises(ParserFailure):run_parser([sys.executable,'-c',command],b'',ParserLimits(wall_seconds=.3))
            pid=int(pidfile.read_text());state=subprocess.run(['ps','-o','stat=','-p',str(pid)],capture_output=True,text=True).stdout.strip()
            self.assertTrue(not state or state.startswith('Z'),state)
    def test_unsupported_hard_memory_and_rich_fallback(self):
        if sys.platform=='darwin':
            with self.assertRaises(ParserFailure):self.project(b'<p>Text</p>',process_limits=ParserLimits(require_hard_memory=True))
        from rich_presentation import project
        with patch('rich_presentation.project_tree',side_effect=ParserFailure('parser-timeout')):
            self.assertEqual(project(dict(html='<p>Text</p>',text='Text'),'a'*32),dict(state='plain-only',text='Text',diagnostics=['parser-resource-failure']))
            with self.assertRaises(ParserFailure):project(dict(html='<p>Text</p>',text='Text'),'a'*32,authoring=True)
