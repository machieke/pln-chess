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


def run(out,work,port=18780):
    out=Path(out).resolve();work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    assert read_json(out/'acceptance.json')['passed']
    with socket.socket() as check:
        check.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        check.bind(('127.0.0.1',port))
    proof=out/'ui';proof.mkdir(exist_ok=True);(out/'ui/verification.json').unlink(missing_ok=True)
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
    argv=[sys.executable,'-m','pln_chess','serve','--checkpoint',str(out/'model/C10-default.json'),'--port',str(port)]
    token=uuid.uuid4().hex;owner_file=work/'owned-server.json';wrapper=work/'owned-server.py'
    wrapper.write_text('import json,os\nfrom pathlib import Path\n'+f"Path({str(owner_file)!r}).write_text(json.dumps({{'pid':os.getpid(),'pgid':os.getpgrp(),'token':{token!r}}}))\n"+f'os.execv({sys.executable!r},{argv!r})\n')
    stream=(proof/'launcher.txt').open('w')
    launch=subprocess.Popen(['proofshot','start','--run','exec '+shlex.join([sys.executable,str(wrapper)]),'--port',str(port),
        '--description','Cycle 10 accepted model, external sources, calibration shift, failure proofs, historical replay, adaptation comparisons, report export and mobile layout'],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    cleanup={};export=None
    try:
        end=time.time()+60
        while not (proof/'.session.json').exists():
            if launch.poll() is not None or time.time()>end:raise RuntimeError('ProofShot startup failed')
            time.sleep(.2)
        session=read_json(proof/'.session.json');viewport(1280,900);cmd('exec','snapshot','-i');cmd('exec','screenshot','initial.png')
        first=submit(model='C8-default',mode='default',fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1',move='c2e2')
        assert 'supported-legal' in first['summary'] and 'operational' in first['summary']
        diagnostic=json.loads(first['diagnostic']);assert diagnostic['calibration']['available'] and not diagnostic['calibration']['native']
        assert diagnostic['raw_native_stv'] and diagnostic['model_version']==read_json(out/'acceptance.json')['model_version']
        checks.append(dict(case='accepted-default-native-values-and-external-calibration',result=first))
        ev("document.getElementById('c10-live').closest('details').scrollIntoView();true");cmd('exec','screenshot','native-and-external-diagnostics.png')
        ev("const p=document.getElementById('c10-live');p.scrollTop=p.scrollHeight;true");cmd('exec','screenshot','empirical-calibration-and-identity.png')
        def load(section,arm='frozen'):
            return ev("(async()=>{document.getElementById('c10-section').value="+json.dumps(section)+";document.getElementById('c10-arm').value="+json.dumps(arm)+";const b=document.getElementById('c10-load');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-detail').textContent);return {available:d.available,section:d.section,arm:d.arm,rows:document.querySelectorAll('#c10-table tbody tr').length,status:document.getElementById('c10-status').textContent,keys:Object.keys(d.data)};})()")
        ev("document.getElementById('c10-study').scrollIntoView();true")
        metrics=load('summary');assert metrics['available'] and metrics['rows']>=4
        checks.append(dict(case='external-source-metric-table',result=metrics))
        complete=ev("document.querySelector('#c10-table tbody tr td:nth-child(2)').textContent")
        ev("document.getElementById('c10-population').value='in_board';document.getElementById('c10-population').dispatchEvent(new Event('change'));true")
        in_board=ev("document.querySelector('#c10-table tbody tr td:nth-child(2)').textContent")
        assert int(in_board)<int(complete);checks.append(dict(case='complete-versus-in-board',complete=complete,in_board=in_board))
        cmd('exec','screenshot','external-source-metrics.png')
        for section in ('provenance','calibration','comparisons','dependence','performance','identity','architecture'):
            result=load(section);assert result['available'] and not result['status'].startswith('Error:')
            checks.append(dict(case='recorded-'+section,result=result))
        load('failures')
        failure=ev("(async()=>{const b=document.getElementById('c10-proof');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-detail').textContent).data;return {fen:d.row.fen,move:d.row.move,classification:d.row.classification,truth_value:d.row.truth_value,proof_id:d.row.proof_id,nodes:d.native_proof_trace.length,evidence:d.supporting_evidence.length};})()")
        assert failure['nodes']>0;checks.append(dict(case='external-failure-proof-and-lineage',result=failure));cmd('exec','screenshot','external-failure-proof.png')
        ev("(async()=>{const b=document.getElementById('c10-use');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));return true;})()")
        reopened=submit();assert failure['classification'] in reopened['summary']
        assert json.loads(reopened['diagnostic'])['raw_native_stv']==failure['truth_value']
        checks.append(dict(case='reopened-frozen-candidate-matches-record',result=reopened))
        ev("document.getElementById('c10-games').closest('details').open=true;document.getElementById('c10-games').scrollIntoView();true")
        games=ev("(async()=>{const b=document.getElementById('c10-games');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));return document.getElementById('c10-game').options.length;})()")
        assert games==150
        game=read_json(out/'datasets/dataset.json')['games'][0];ply=min(12,len(game['moves'])-1)
        replayed=ev("(async()=>{document.getElementById('c10-ply').value="+str(ply)+";const b=document.getElementById('c10-replay');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-history').textContent);return {events:d.events.length,fen:d.resulting_fen,status:d.status,legality:d.historical_legality,model:d.model_version};})()")
        assert replayed['events']==ply and replayed['legality']=='unverified'
        checks.append(dict(case='published-game-event-replay',result=replayed));cmd('exec','screenshot','published-game-history.png')
        ev("document.getElementById('c10-history-use').click();true")
        historical=submit(move=game['moves'][ply]);live=json.loads(historical['diagnostic'])
        assert not historical['status'].startswith('Error:') and live['history_status']=='structurally-consistent'
        assert not live['calibration']['available']
        checks.append(dict(case='supplied-history-native-inference-and-calibration-scope',result=historical))
        ev("document.getElementById('c10-control').closest('details').open=true;document.getElementById('c10-control').scrollIntoView();true")
        control=ev("(async()=>{const b=document.getElementById('c10-control');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-detail').textContent).data;return {id:d.id,geometry:d.identical_geometry,left:d.left.candidate.classification,right:d.right.candidate.classification,removed:d.removed_temporal_channel.candidate.classification};})()")
        assert control['geometry'];checks.append(dict(case='temporal-counterfactual-and-removal-control',result=control));cmd('exec','screenshot','temporal-counterfactual.png')
        submit(model='C8-default',mode='operational',fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1',move='c2e2',history='{}',**{'temporal-mode':'fen-only'})
        ev("document.getElementById('c10-compare').closest('details').open=true;document.getElementById('c10-compare').scrollIntoView();true")
        compared=ev("(async()=>{const b=document.getElementById('c10-compare');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));const d=JSON.parse(document.getElementById('c10-detail').textContent);return {models:Object.keys(d.comparisons),selected:d.selected_key,mode:d.selected_mode,promoted:d.new_learning_promoted,calibration:Object.fromEntries(Object.entries(d.comparisons).map(([k,v])=>[k,v.candidate.external_diagnostics.available]))};})()")
        assert compared['models']==['frozen','small','large'] and compared['selected']=='frozen' and not compared['promoted']
        assert compared['calibration']==dict(frozen=True,small=False,large=False)
        checks.append(dict(case='three-model-comparison-and-calibration-boundary',result=compared));cmd('exec','screenshot','experimental-model-comparison.png')
        experimental=submit(model='C10-small',mode='default');assert 'strict' in experimental['summary'] and 'unknown' in experimental['summary']
        checks.append(dict(case='unpromoted-adaptation-defaults-strict',result=experimental))
        incomplete=submit(model='C8-default',mode='operational',**{'max-invocations':0});assert 'incomplete' in incomplete['summary'] and not json.loads(incomplete['diagnostic'])['calibration']['available']
        checks.append(dict(case='budget-incomplete-is-distinct',result=incomplete))
        invalid=submit(history='{');assert invalid['status'].startswith('Error:') and invalid['diagnostic']==''
        checks.append(dict(case='invalid-JSON-clears-native-and-empirical-output',result=invalid))
        submit(history='{}',**{'max-invocations':20000})
        load('calibration')
        export=ev("(async()=>{const old=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.c10Blob=b;return old(b)};document.getElementById('c10-export').click();window.c10Text=await window.c10Blob.text();const bytes=new TextEncoder().encode(window.c10Text);const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');return {bytes:bytes.length,characters:window.c10Text.length,sha256:hash}})()")
        raw=''.join(ev(f'window.c10Text.slice({i},{i+100000})') for i in range(0,export['characters'],100000)).encode()
        assert hashlib.sha256(raw).hexdigest()==export['sha256'];assert json.loads(raw)['data']['fit_games']==24
        (proof/'browser-calibration-export.json').write_bytes(raw);checks.append(dict(case='actual-external-calibration-export',result=export))
        legacy=ev("(async()=>{const b=document.getElementById('c9-load');b.click();while(b.disabled)await new Promise(r=>setTimeout(r,100));return document.querySelectorAll('#c9-table tbody tr').length;})()")
        assert legacy>=5;checks.append(dict(case='legacy-Cycle9-inspector-preserved',rows=legacy))
        viewport(390,844)
        mobile=ev("document.getElementById('c10-study').scrollIntoView();({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})")
        write_json(proof/'mobile-layout.json',mobile);cmd('exec','screenshot','mobile-external-study.png')
        assert mobile['width']==390 and mobile['scrollWidth']<=390,mobile
        checks.append(dict(case='mobile-external-study-layout',result=mobile))
        # The full accessibility tree can exceed the browser tool's CDP limit
        # after raw proof/calibration JSON has accumulated. Keep the loaded-page
        # functional assertions, export and screenshots above, then inspect the
        # initial mobile controls through normal navigation to a fresh page.
        cmd('exec','open',f'http://127.0.0.1:{port}')
        controls=cmd('exec','snapshot','-i','-s','#c10-study')
        assert 'Load external report' in controls and 'Export external JSON' in controls
        checks.append(dict(case='fresh-mobile-accessibility-controls',
            scope='Fresh page after loaded-page functionality, layout, screenshots and export checks. Full loaded-page accessibility tree is not certified.'))
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
    write_json(out/'ui/verification.json',dict(passed=True,source_hash=production_code_hash(),checks=checks,errors=errors,
        actual_export=export,server_cleanup=cleanup,session_dir=str(Path(session['sessionDir']).relative_to(out))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--work',required=True);p.add_argument('--port',type=int,default=18780)
    a=p.parse_args();run(a.out,a.work,a.port)
