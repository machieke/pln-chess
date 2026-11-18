"""Single-owner pipe to the pinned PeTTa string API and native state cell."""
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import tempfile
import time
from pln_chess.common import digest
from pln_chess.pln import Runtime
from research.cycle15.native_reasoner import Budgets,parse
from .meter import reserve
from .native import fresh_input,materialize,derive_expression,finish,prints
from .state import query_list,tv_stamps

class Session:
    def __init__(self,meter=None,phase='residency-probe'):
        self.runtime=Runtime(); self.meter=meter;self.phase=phase
        self.frames=[];self.current=None;self.proc=None

    def __enter__(self):
        rt=self.runtime
        if self.meter:reserve(self.meter,self.phase)
        self.errors=tempfile.TemporaryFile()
        self.proc=subprocess.Popen(['swipl','--stack_limit=8g','-q','-f','none','-s',str(Path(__file__).with_name('frames.pl')),
            '-g','cycle20_frames','-t','halt','--',str(rt.runner.parent/'src/main.pl'),str(rt.library),'--silent'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.errors,start_new_session=True,bufsize=0)
        try:self._until(b'C20READY\n',15)
        except BaseException:
            self.close();raise
        return self

    def _until(self,end,timeout):
        deadline=time.monotonic()+timeout;chunks=bytearray()
        while not chunks.endswith(end):
            remaining=deadline-time.monotonic()
            if remaining<=0 or not select.select([self.proc.stdout],[],[],remaining)[0]:raise TimeoutError('Resident response timed out')
            data=os.read(self.proc.stdout.fileno(),65536)
            if not data:
                self.errors.seek(0);raise RuntimeError('Resident process ended: '+self.errors.read().decode()[-2000:])
            chunks.extend(data)
            if len(chunks)>16*1024*1024:raise ValueError('Oversized native response')
        return chunks[:-len(end)].decode()

    def _request(self,program,timeout):
        if self.proc is None or self.proc.poll() is not None:raise ValueError('Resident session is closed')
        sequence=len(self.frames)+1;start=time.perf_counter()
        frame=(json.dumps(dict(id=sequence,code=program))+'\n').encode()
        if len(frame)>2*1024*1024:raise ValueError('Oversized native input')
        try:
            deadline=time.monotonic()+timeout
            remaining_frame=memoryview(frame)
            os.set_blocking(self.proc.stdin.fileno(),False)
            while remaining_frame:
                remaining=deadline-time.monotonic()
                if remaining<=0 or not select.select([],[self.proc.stdin],[],remaining)[1]:
                    raise TimeoutError('Resident request timed out')
                sent=os.write(self.proc.stdin.fileno(),remaining_frame[:65536])
                remaining_frame=remaining_frame[sent:]
            stdout=self._until(f'C20DONE {sequence}\n'.encode(),deadline-time.monotonic())
            value=dict(program=program,stdout=stdout,runtime=self.runtime.manifest,incomplete=False,
                       input_bytes=len(frame),output_bytes=len(stdout.encode()),pid=self.proc.pid,
                       sequence=sequence,wall_seconds=time.perf_counter()-start)
            self.frames.append(value)
            return value
        except BaseException:
            self.close();raise

    def load(self,workspace,queries,budget):
        if self.current is not None:raise ValueError('Generation already loaded')
        queries=query_list(queries);inputs,defs=fresh_input(workspace.facts,workspace.rules)
        code=defs+materialize(derive_expression('(c20tasks)','(c20beliefs)',budget),queries,save=True)
        try:
            result=finish(self._request(code,budget.timeout),queries,workspace.identity,inputs,budget,1)
            self.current=result['state'];self.identity=workspace.identity
            return result
        except BaseException:
            self.close();raise

    def _require(self,identity,snapshot):
        if self.proc is None or self.current is None or identity!=self.identity or snapshot!=self.current['snapshot']:
            raise ValueError('Unavailable resident generation')

    def read(self,identity,snapshot,queries):
        self._require(identity,snapshot);qs=query_list(queries)
        receipt=self._request('!(let ($remaining $retained) (get-state &c20) (progn '+prints(qs)+'))',30)
        results=[]
        try:
            for line in receipt['stdout'].splitlines():
                if line.startswith('(C20DERIVE') or line.startswith('(SELECTED '):raise ValueError('Unexpected derivation during resident read')
                if line.startswith('(C20READ '):
                    _,i,value=parse(line)
                    if i!=str(len(results)):raise ValueError('Resident readout order')
                    results.append(dict(query=qs[int(i)],answer=tv_stamps(*value) if value else None,
                                        snapshot=snapshot,generation=self.current['identity'],native_receipt=digest(receipt)))
            if len(qs)!=len(results):raise ValueError('Missing resident answer')
            return results
        except BaseException:
            self.close();raise

    def advance(self,identity,snapshot,queries,steps):
        self._require(identity,snapshot);qs=query_list(queries)
        b=Budgets(steps,**self.current['capacities'],timeout=30)
        expr='(let ($oldtasks $oldbeliefs) (get-state &c20) '+derive_expression('$oldtasks','$oldbeliefs',b)+')'
        try:
            result=finish(self._request(materialize(expr,qs,save=True),b.timeout),qs,identity,self.current['inputs'],b,1,self.current)
            self.current=result['state'];return result
        except BaseException:
            self.close();raise

    def close(self):
        if self.proc is not None:
            try:
                self.proc.stdin.close()
                self.proc.wait(timeout=2)
            except (BrokenPipeError,subprocess.TimeoutExpired):
                if self.proc.poll() is None:os.killpg(self.proc.pid,signal.SIGKILL)
                self.proc.wait()
            finally:
                self.proc.stdout.close();self.errors.close();self.proc=None;self.current=None

    def __exit__(self,*exc):self.close()
