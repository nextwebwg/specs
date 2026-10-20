"""Explicit local adapter for a separately pinned parse5 module; not a network API."""
import json
from pathlib import Path
import sys
from dataclasses import asdict
from parser_process import ParserLimits,run_parser
from xml.etree.ElementTree import Element

def parser_adapter(module_url,*,process_limits=None,node_heap_mib=128):
    limits=ParserLimits() if process_limits is None else process_limits
    if not isinstance(limits,ParserLimits) or type(node_heap_mib)is not int or node_heap_mib<1:raise ValueError('Explicit parser limits required')
    def parse(text):
        output=run_parser([sys.executable,str(Path(__file__).with_name('parse5_worker.py')),json.dumps(asdict(limits)),str(node_heap_mib),str(Path(__file__).with_name('parse5-tree.mjs')),module_url],json.dumps(text).encode(),limits)
        data=json.loads(output)
        def element(node):
            result=Element(node['tag'],node.get('attributes',{}))
            previous=None
            for child in node['children']:
                if isinstance(child,str):
                    if previous is None:result.text=(result.text or '')+child
                    else:previous.tail=(previous.tail or '')+child
                else:
                    previous=element(child);result.append(previous)
            return result
        try:return element(data['root']),[(None,code,{}) for code in data['errors']]
        except RecursionError as error:raise ValueError('Parser result depth') from error
    return parse
