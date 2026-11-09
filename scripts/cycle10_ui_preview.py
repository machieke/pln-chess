"""Recorded local browser checks for empirical diagnostics and native boundaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
import uuid
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash


def run(out,work,port=18781):
    out=Path(out).resolve();work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    with socket.socket() as check:
        check.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        check.bind(('127.0.0.1',port))
    proof=out/'ui-preview';proof.mkdir(exist_ok=True);(out/'ui-preview/verification.json').unlink(missing_ok=True)
    write_json(work/'proofshot.config.json',dict(output=str(proof),viewport=dict(width=1280,height=900)))
    env=dict(os.environ,C10_OUT=str(out),TMPDIR='/dev/shm',AGENT_BROWSER_SESSION='pln-chess-cycle10-'+uuid.uuid4().hex[:12]);env.pop('C8_OUT',None)
    commands=[];checks=[];errors={};session=None
    def cmd(*args,structured=False):
        start=time.time();p=subprocess.run(['proofshot',*args],cwd=work,env=env,capture_output=True,text=True,timeout=60)
        commands.append(dict(args=list(args),returncode=p.returncode,seconds=time.time()-start,
            stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),stderr=p.stderr))
        write_json(proof/'commands.json',commands)
        if p.returncode:raise RuntimeError((args,p.stderr,p.stdout[:1500]))
        return json.loads(p.stdout) if structured else p.stdout
    def ev(code):return cmd('exec','eval',code,structured=True)
    def viewport(w,h):
        for _ in range(3):
            cmd('exec','--session',env['AGENT_BROWSER_SESSION'],'set','viewport',str(w),str(h))
            actual=ev(f'(async()=>{{const end=Date.now()+5000;while((innerWidth!=={w}||innerHeight!=={h})&&Date.now()<end)await new Promise(r=>setTimeout(r,100));return [innerWidth,innerHeight]}})()')
            if actual==[w,h]:return
        raise AssertionError(('Viewport mismatch',actual,w,h))
    def submit(**fields):
        return ev("(async()=>{const fields="+json.dumps(fields)+";for(const [id,value] of Object.entries(fields)){const e=document.getElementById(id);if(typeof value==='boolean')e.checked=value;else e.value=value;}document.getElementById('form').requestSubmit();while(document.getElementById('run').disabled)await new Promise(r=>setTimeout(r,100));return {status:document.getElementById('status').textContent,summary:document.getElementById('summary').textContent,diagnostic:document.getElementById('c10-live').textContent};})()")
    argv=[sys.executable,'-m','pln_chess','serve','--checkpoint',str(ROOT/'artifacts/cycle8/model/C8-default.json'),'--port',str(port)]
    token=uuid.uuid4().hex;owner_file=work/'owned-server.json';wrapper=work/'owned-server.py'
    wrapper.write_text('import json,os\nfrom pathlib import Path\n'+f"Path({str(owner_file)!r}).write_text(json.dumps({{'pid':os.getpid(),'pgid':os.getpgrp(),'token':{token!r}}}))\n"+f'os.execv({sys.executable!r},{argv!r})\n')
    stream=(proof/'launcher.txt').open('w')
    launch=subprocess.Popen(['proofshot','start','--run','exec '+shlex.join([sys.executable,str(wrapper)]),'--port',str(port),
        '--description','Cycle 10 read-only source provenance and structural event replay, desktop/mobile; no native inference during benchmark'],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    cleanup={};export=None
    try:
        end=time.time()+60
        while not (proof/'.session.json').exists():
            if launch.poll() is not None or time.time()>end:raise RuntimeError('ProofShot startup failed')
            time.sleep(.2)
        session=read_json(proof/'.session.json');viewport(1280,900);cmd('exec','snapshot','-i');cmd('exec','screenshot','initial.png')
        ev("document.getElementById('c10-study').scrollIntoView();true")
        sources=ev("(async()=>{document.getElementById('c10-section').value='provenance';const b=document.getElementById('c10-load');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-detail').textContent);return {sources:d.data.sources.length,status:document.getElementById('c10-status').textContent};})()")
        assert sources['sources']==3 and not sources['status'].startswith('Error:')
        checks.append(dict(case='actual-source-provenance',result=sources));cmd('exec','screenshot','desktop-source-provenance.png')
        ev("document.getElementById('c10-games').closest('details').open=true;document.getElementById('c10-games').scrollIntoView();true")
        games=ev("(async()=>{const b=document.getElementById('c10-games');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));return document.getElementById('c10-game').options.length;})()")
        assert games==150;checks.append(dict(case='actual-source-game-index',games=games))
        history=ev("(async()=>{const b=document.getElementById('c10-replay');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-history').textContent);return {events:d.events.length,status:d.status,legality:d.historical_legality};})()")
        assert history['events']==12 and history['legality']=='unverified'
        checks.append(dict(case='structural-event-display-without-native-inference',result=history));cmd('exec','screenshot','desktop-event-history.png')
        viewport(390,844)
        mobile=ev("document.getElementById('c10-study').scrollIntoView();({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})")
        assert mobile['width']==390 and mobile['scrollWidth']<=390,mobile
        checks.append(dict(case='mobile-layout',result=mobile));cmd('exec','screenshot','mobile-source-and-history.png');cmd('exec','snapshot','-i')
    finally:
        try:
            if session:
                stopped=cmd('stop');(proof/'stop.txt').write_text(stopped)
                for kind in ('Console','Server'):
                    match=re.search(kind+r' errors:\s+(\d+)',stopped);errors[kind.lower()]=int(match[1]) if match else None
        finally:
            if owner_file.exists():
                owned=read_json(owner_file);assert owned['token']==token
                cleanup=dict(pid=owned['pid'],pgid=owned['pgid'],ownership_token_matched=True)
                try:
                    actual=Path(f"/proc/{owned['pid']}/cmdline").read_bytes().rstrip(b'\0').split(b'\0')
                    assert actual==[a.encode() for a in argv] and os.getpgid(owned['pid'])==owned['pgid']
                    os.killpg(owned['pgid'],signal.SIGTERM)
                except (ProcessLookupError,FileNotFoundError):pass
            try:os.killpg(launch.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            stream.close()
    end=time.time()+5
    while True:
        with socket.socket() as check:check.settimeout(.2);listening=check.connect_ex(('127.0.0.1',port))==0
        if not listening:break
        assert time.time()<end,'Owned verification server remained listening';time.sleep(.1)
    cleanup['port_closed']=True;assert errors==dict(console=0,server=0),errors
    write_json(out/'ui-preview/verification.json',dict(passed=True,source_hash=production_code_hash(),checks=checks,errors=errors,
        actual_export=export,server_cleanup=cleanup,session_dir=str(Path(session['sessionDir']).relative_to(out))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--work',required=True);p.add_argument('--port',type=int,default=18781)
    a=p.parse_args();run(a.out,a.work,a.port)
