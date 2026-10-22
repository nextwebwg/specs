"""Trusted entry point: install process limits before importing the HTML parser."""
import json,sys
from parser_process import ParserLimits,install_worker_limits
limits=ParserLimits(**json.loads(sys.argv[1]));install_worker_limits(limits)
from html_tree import _project_tree_local
request=json.loads(sys.stdin.buffer.read())
try:
    result=_project_tree_local(request['text'].encode('utf-8'),mime_charset='utf-8',max_bytes=request['max_bytes'],max_nodes=request['max_nodes'],max_depth=request['max_depth'])
except ValueError as error:
    # Return only this fixed semantic category, never source or a partial tree.
    # Other worker errors retain the existing bounded rejection boundary.
    if not str(error).startswith('unpreserved-direction-boundary:'):raise
    result={'failure':'unpreserved-direction-boundary'}
sys.stdout.write(json.dumps(result,ensure_ascii=True))
