"""Exec Node in the already bounded worker; no nested parser process."""
import json,os,sys,resource
from parser_process import ParserLimits
limits=ParserLimits(**json.loads(sys.argv[1]));limits.validate()
if limits.require_hard_memory:raise ValueError('Node heap cap is not a hard process-memory ceiling')
resource.setrlimit(resource.RLIMIT_CPU,(limits.cpu_seconds,limits.cpu_seconds))
resource.setrlimit(resource.RLIMIT_FSIZE,(limits.max_output,limits.max_output))
os.execvp('node',['node','--max-old-space-size='+sys.argv[2],*sys.argv[3:]])
