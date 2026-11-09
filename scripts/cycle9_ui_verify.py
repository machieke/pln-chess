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


def run(out,work,port=18779):
    out=Path(out).resolve();work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    assert read_json(out/'acceptance.json')['passed']
    with socket.socket() as check:check.bind(('127.0.0.1',port))
    proof=out/'ui';proof.mkdir(exist_ok=True);(out/'ui-verification.json').unlink(missing_ok=True)
    write_json(work/'proofshot.config.json',dict(output=str(proof),viewport=dict(width=1280,height=900)))
    env=dict(os.environ,C9_OUT=str(out),TMPDIR='/dev/shm',AGENT_BROWSER_SESSION='pln-chess-cycle9-'+uuid.uuid4().hex[:12]);env.pop('C8_OUT',None)
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
        return ev("(async()=>{const fields="+json.dumps(fields)+";for(const [id,value] of Object.entries(fields)){const e=document.getElementById(id);if(typeof value==='boolean')e.checked=value;else e.value=value;}document.getElementById('form').requestSubmit();while(document.getElementById('run').disabled)await new Promise(r=>setTimeout(r,100));return {status:document.getElementById('status').textContent,summary:document.getElementById('summary').textContent,diagnostic:document.getElementById('c9-live').textContent};})()")
    argv=[sys.executable,'-m','pln_chess','serve','--checkpoint',str(out/'model/C9-default.json'),'--port',str(port)]
    token=uuid.uuid4().hex;owner_file=work/'owned-server.json';wrapper=work/'owned-server.py'
    wrapper.write_text('import json,os\nfrom pathlib import Path\n'+f"Path({str(owner_file)!r}).write_text(json.dumps({{'pid':os.getpid(),'pgid':os.getpgrp(),'token':{token!r}}}))\n"+f'os.execv({sys.executable!r},{argv!r})\n')
    stream=(proof/'launcher.txt').open('w')
    launch=subprocess.Popen(['proofshot','start','--run','exec '+shlex.join([sys.executable,str(wrapper)]),'--port',str(port),
        '--description','Cycle 9 accepted model, calibrated diagnostics, failure provenance, report export, temporal categories and mobile layout'],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    cleanup={};export=None
    try:
        end=time.time()+60
        while not (proof/'.session.json').exists():
            if launch.poll() is not None or time.time()>end:raise RuntimeError('ProofShot startup failed')
            time.sleep(.2)
        session=read_json(proof/'.session.json');viewport(1280,900);cmd('exec','snapshot','-i');cmd('exec','screenshot','initial.png')
        first=submit(model='C8-default',mode='default',fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1',move='c2e2')
        assert 'supported-legal' in first['summary'] and 'operational' in first['summary']
        diagnostic=json.loads(first['diagnostic']);assert diagnostic['calibrated']['native'] is False and diagnostic['calibrated']['available']
        assert diagnostic['model_version']==read_json(out/'acceptance.json')['model_version']
        checks.append(dict(case='accepted-model-and-distinct-calibration',result=first))
        assert ev("document.getElementById('c9-live').scrollIntoView();document.getElementById('c9-live').offsetParent!==null")
        cmd('exec','screenshot','native-and-empirical-diagnostics.png')
        ev("document.getElementById('c9-study').scrollIntoView();true")
        loaded=ev("(async()=>{document.getElementById('c9-load').click();while(document.getElementById('c9-load').disabled)await new Promise(r=>setTimeout(r,100));return {rows:document.querySelectorAll('#c9-table tbody tr').length,status:document.getElementById('c9-status').textContent}})()")
        assert loaded['rows']>=5 and not loaded['status'].startswith('Error:');checks.append(dict(case='cohort-table',result=loaded))
        ev("document.getElementById('c9-population').value='in_board';document.getElementById('c9-population').dispatchEvent(new Event('change'));true")
        cmd('exec','screenshot','cohort-comparison.png')
        failures=ev("(async()=>{document.getElementById('c9-failures').click();while(document.getElementById('c9-failures').disabled)await new Promise(r=>setTimeout(r,100));document.getElementById('c9-proof').click();while(document.getElementById('c9-proof').disabled)await new Promise(r=>setTimeout(r,100));return JSON.parse(document.getElementById('c9-detail').textContent)})()")
        assert failures['data']['proof_trace'] and failures['data']['row']['evidence_ids']
        checks.append(dict(case='failure-native-proof-navigation',proof_hash=failures['data']['row']['proof_id']))
        cmd('exec','screenshot','failure-proof.png')
        calibration=ev("(async()=>{document.getElementById('c9-calibration').click();while(document.getElementById('c9-calibration').disabled)await new Promise(r=>setTimeout(r,100));return JSON.parse(document.getElementById('c9-detail').textContent)})()")
        assert calibration['native'] is False and calibration['data']['fit_games']==20
        export=ev("(async()=>{const old=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.c9Blob=b;return old(b)};document.getElementById('c9-export').click();window.c9Text=await window.c9Blob.text();const bytes=new TextEncoder().encode(window.c9Text);const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');return {bytes:bytes.length,characters:window.c9Text.length,sha256:hash}})()")
        raw=''.join(ev(f'window.c9Text.slice({i},{i+100000})') for i in range(0,export['characters'],100000)).encode()
        assert hashlib.sha256(raw).hexdigest()==export['sha256'];assert json.loads(raw)['section']=='calibration'
        (proof/'browser-calibration-export.json').write_bytes(raw);checks.append(dict(case='actual-calibration-export',result=export))
        strict=submit(mode='strict');assert 'unknown' in strict['summary'] and not json.loads(strict['diagnostic'])['calibrated']['available']
        checks.append(dict(case='strict-distinction',result=strict))
        incomplete=submit(mode='operational',**{'max-invocations':0});assert 'incomplete' in incomplete['summary']
        assert not json.loads(incomplete['diagnostic'])['calibrated']['available'];checks.append(dict(case='incomplete-boundary',result=incomplete))
        temporal=submit(mode='operational',**{'max-invocations':20000,'temporal-mode':'trusted-metadata','history':json.dumps(dict(source='browser-metadata',confidence=.8))})
        t=json.loads(temporal['diagnostic'])['temporal_categories'];assert t['trusted_state_metadata'] and not t['directly_observed_events']
        checks.append(dict(case='temporal-metadata-distinction',schema=t['schema']))
        invalid=submit(history='{');assert invalid['status'].startswith('Error:') and invalid['diagnostic']==''
        checks.append(dict(case='invalid-input-clears-live-diagnostics',result=invalid))
        submit(history='{}',**{'temporal-mode':'fen-only'});viewport(390,844)
        mobile=ev("document.getElementById('c9-study').scrollIntoView();({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})")
        assert mobile['width']==390 and mobile['scrollWidth']<=390
        cmd('exec','screenshot','mobile-study.png');checks.append(dict(case='mobile-layout',result=mobile));cmd('exec','snapshot','-i')
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
    write_json(out/'ui-verification.json',dict(passed=True,source_hash=production_code_hash(),checks=checks,errors=errors,
        actual_export=export,server_cleanup=cleanup,session_dir=str(Path(session['sessionDir']).relative_to(out))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--work',required=True);p.add_argument('--port',type=int,default=18779)
    a=p.parse_args();run(a.out,a.work,a.port)
