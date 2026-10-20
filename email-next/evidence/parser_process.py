"""Disposable parser process: limits are local policy, not a sandbox."""
from dataclasses import dataclass,asdict
import json,math,os,signal,subprocess,tempfile,threading
@dataclass(frozen=True)
class ParserLimits:
    wall_seconds:float=5
    cpu_seconds:int=3
    max_output:int=4194304
    max_resident:int=268435456
    sample_seconds:float=0.02
    require_hard_memory:bool=False
    def validate(self):
        if any(type(v)is not int or v<1 for v in (self.cpu_seconds,self.max_output,self.max_resident)):raise ValueError('Positive parser integer limits required')
        if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in (self.wall_seconds,self.sample_seconds)):raise ValueError('Positive finite parser durations required')
        if type(self.require_hard_memory)is not bool:raise ValueError('Explicit hard-memory policy')

class ParserFailure(ValueError):pass

def install_worker_limits(limits):
    import resource,sys
    limits.validate()
    resource.setrlimit(resource.RLIMIT_CPU,(limits.cpu_seconds,limits.cpu_seconds))
    resource.setrlimit(resource.RLIMIT_FSIZE,(limits.max_output,limits.max_output))
    if sys.platform.startswith('linux'):
        resource.setrlimit(resource.RLIMIT_AS,(limits.max_resident,limits.max_resident))
    elif limits.require_hard_memory:raise ParserFailure('hard-memory-enforcement-unavailable')

def run_parser(command,input_bytes,limits):
    limits.validate()
    if not isinstance(input_bytes,bytes):raise ValueError('Parser input bytes required')
    with tempfile.TemporaryFile() as output:
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=output,stderr=subprocess.DEVNULL,start_new_session=True)
        stopped=threading.Event();failure=[]
        def kill():
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        def monitor():
            while not stopped.is_set() and process.poll() is None:
                try:
                    result=subprocess.run(['ps','-o','rss=','-p',str(process.pid)],capture_output=True,text=True,timeout=min(1,limits.wall_seconds))
                    if process.poll() is not None:return
                    if result.returncode or not result.stdout.strip():raise ValueError('RSS unavailable')
                    if int(result.stdout.strip())*1024>limits.max_resident:failure.append('resident-watchdog');kill();return
                except (ValueError,OSError,subprocess.SubprocessError):
                    if process.poll() is None:failure.append('resident-monitor-unavailable');kill()
                    return
                stopped.wait(limits.sample_seconds)
        watcher=threading.Thread(target=monitor,daemon=True);watcher.start()
        try:
            try:process.communicate(input_bytes,timeout=limits.wall_seconds)
            except subprocess.TimeoutExpired:failure.append('parser-timeout');kill();process.communicate()
        finally:
            stopped.set();watcher.join(timeout=2);kill()
            # A timed-out partial write can leave stdin open when communicate()
            # resumes without input. Reap even exceptional exits and close the
            # parent's pipe explicitly; worker termination alone cannot close it.
            try:process.wait()
            finally:
                if process.stdin is not None:
                    try:process.stdin.close()
                    except BrokenPipeError:pass
        if failure:raise ParserFailure(failure[0])
        if process.returncode:raise ParserFailure('parser-worker-rejected')
        if output.tell()>limits.max_output:raise ParserFailure('parser-output-limit')
        output.seek(0);result=output.read(limits.max_output+1)
        if len(result)>limits.max_output:raise ParserFailure('parser-output-limit')
        return result
