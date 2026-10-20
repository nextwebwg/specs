"""Trusted entry point: install process limits before importing the HTML parser."""
import json,sys
from parser_process import ParserLimits,install_worker_limits
limits=ParserLimits(**json.loads(sys.argv[1]));install_worker_limits(limits)
from html_tree import _project_tree_local
request=json.loads(sys.stdin.buffer.read())
result=_project_tree_local(request['text'].encode('utf-8'),mime_charset='utf-8',max_bytes=request['max_bytes'],max_nodes=request['max_nodes'],max_depth=request['max_depth'])
sys.stdout.write(json.dumps(result,ensure_ascii=True))
