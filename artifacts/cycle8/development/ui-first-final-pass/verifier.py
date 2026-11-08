"""Real-browser ProofShot verification; local server, recording and complete export."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle3 import read_gzip


def run(out,work,port=18769):
    out=Path(out).resolve();work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    acceptance=read_json(out/'acceptance.json');assert acceptance['passed']
    accepted_cases={r['move']:r['candidate'] for r in read_gzip(out/f"proofs/{acceptance['selected_variant']}-original-errors.json.xz")}
    # ProofShot can kill an occupied port; establish that this port is free first.
    with socket.socket() as check:check.bind(('127.0.0.1',port))
    proof=out/'ui';proof.mkdir(parents=True,exist_ok=True)
    write_json(work/'proofshot.config.json',{'output':str(proof),'viewport':{'width':1280,'height':900}})
    env=dict(os.environ,C8_OUT=str(out),TMPDIR='/dev/shm',AGENT_BROWSER_SESSION='pln-chess-cycle8-final')
    receipts=[]
    def cmd(*args,structured=False):
        start=time.time();p=subprocess.run(['proofshot',*args],cwd=work,env=env,capture_output=True,text=True,timeout=60)
        receipts.append({'args':list(args),'returncode':p.returncode,'seconds':time.time()-start,
            'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'stdout_bytes':len(p.stdout.encode()),'stderr':p.stderr})
        write_json(proof/'command-receipts.json',receipts)
        if p.returncode:raise RuntimeError((args,p.stderr,p.stdout[:2000]))
        return json.loads(p.stdout) if structured else p.stdout
    def evaluate(code):return cmd('exec','eval',code,structured=True)
    def submit(**fields):
        code="(async()=>{const values="+json.dumps(fields)+";for(const [key,value] of Object.entries(values)){const e=document.getElementById(key);if(typeof value==='boolean')e.checked=value;else e.value=value;}document.getElementById('form').requestSubmit();while(document.getElementById('run').disabled)await new Promise(r=>setTimeout(r,100));return {status:document.getElementById('status').textContent,title:document.getElementById('title').textContent,comparison:document.getElementById('model-comparison').textContent,rawEmpty:document.getElementById('raw').textContent===''};})()"
        return evaluate(code)
    launch=' '.join(['C8_OUT='+shlex.quote(str(out)),'TMPDIR=/dev/shm',shlex.join([sys.executable,'-m','pln_chess','serve','--checkpoint',str(out/'model/C8-default.json'),'--port',str(port)])])
    stream=(proof/'launcher.txt').open('w');process=subprocess.Popen(['proofshot','start','--run',launch,'--port',str(port),'--description','Cycle 8 accepted default, all eight promotion comparisons, modes, budget, export and mobile layout'],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    session=None;results=[];export_meta=None;errors={}
    try:
        deadline=time.time()+60
        while not (proof/'.session.json').exists():
            if process.poll() is not None or time.time()>deadline:raise RuntimeError('ProofShot did not start; inspect launcher.txt')
            time.sleep(.2)
        session=read_json(proof/'.session.json')
        cmd('exec','--session',env['AGENT_BROWSER_SESSION'],'set','viewport','1280','900')
        cmd('exec','snapshot','-i');cmd('exec','screenshot','before.png')
        initial=submit(model='C8-default',mode='default',fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1',move='c2e2')
        assert initial['title']=='c2e2 · Rook' and 'supported-legal' in evaluate("document.getElementById('summary').textContent")
        results.append({'case':'accepted-default','result':initial})
        promotion='r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29'
        for destination in ('f8','e8'):
            for choice in ('q','r','b','n'):
                move='f7'+destination+choice;r=submit(model='C8-default',mode='operational',fen=promotion,move=move,**{'compare-models':True})
                assert not r['status'].startswith('Error:'),r
                comparison=json.loads(r['comparison']);expected='supported-legal' if destination=='e8' else 'supported-illegal'
                assert comparison['C8-experimental']['classification']==expected
                if acceptance['new_learning_promoted']:
                    assert comparison['C8-accepted']['classification']==accepted_cases[move]['classification']
                    assert comparison['C8-accepted']['proof_complete']==accepted_cases[move]['proof_complete']
                assert comparison['C7-operational']['classification']=='unknown'
                assert comparison['C7-learned-experimental']['classification']==('supported-illegal' if destination=='e8' else 'supported-legal')
                assert not comparison['C8-experimental']['proof_complete'] if destination=='e8' else comparison['C8-experimental']['proof_complete']
                results.append({'case':move,'classifications':{k:v['classification'] for k,v in comparison.items()},'raw_native_STVs':{k:v['truth_value'] for k,v in comparison.items()}})
                if choice=='n':
                    evaluate("document.getElementById('mode-table').scrollIntoView();true")
                    cmd('exec','screenshot',destination+'-comparison.png')
                print('browser',move,'passed',flush=True)
        panel=evaluate("document.getElementById('promotion').parentElement.open=true;document.getElementById('promotion').scrollIntoView();JSON.parse(document.getElementById('promotion').textContent)")
        assert panel['transition']['descriptor']['resulting_piece']=='Knight'
        assert panel['transition']['descriptor']['destination_kind']=='Knight'
        assert panel['positive_proof_complete'] is False
        cmd('exec','screenshot','promotion-evidence.png')
        results.append({'case':'promotion-evidence-panel','descriptor':panel['transition']['descriptor'],'positive_proof_complete':panel['positive_proof_complete']})
        # Intercept the actual export Blob while preserving the browser's real download behavior.
        export_meta=evaluate("(async()=>{const original=URL.createObjectURL.bind(URL);URL.createObjectURL=blob=>{window.c8ExportBlob=blob;return original(blob)};document.getElementById('export-diagnostic').click();window.c8ExportText=await window.c8ExportBlob.text();const bytes=new TextEncoder().encode(window.c8ExportText);const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');return {bytes:bytes.length,characters:window.c8ExportText.length,sha256:hash};})()")
        chunks=[evaluate(f'window.c8ExportText.slice({i},{i+100000})') for i in range(0,export_meta['characters'],100000)]
        raw=''.join(chunks).encode();assert hashlib.sha256(raw).hexdigest()==export_meta['sha256'] and len(raw)==export_meta['bytes']
        exported=json.loads(raw);assert all(r['candidate']['proof_trace'] for r in exported['comparisons'].values())
        (proof/'browser-comparison-export.json').write_bytes(raw)
        strict=submit(mode='strict',**{'compare-models':False})
        assert 'unknown' in evaluate("document.getElementById('summary').textContent")
        results.append({'case':'strict-positive-abstention','result':strict})
        incomplete=submit(mode='operational',**{'max-invocations':0})
        assert 'incomplete' in evaluate("document.getElementById('summary').textContent")
        cmd('exec','screenshot','incomplete.png');results.append({'case':'zero-budget','result':incomplete})
        invalid=submit(history='{');assert invalid['status'].startswith('Error:') and invalid['rawEmpty']
        assert evaluate("document.getElementById('title').textContent")=='No inference result'
        results.append({'case':'invalid-history-json-clears-results','result':invalid})
        submit(history='{}',mode='operational',**{'max-invocations':20000,'compare-models':True})
        cmd('exec','--session',env['AGENT_BROWSER_SESSION'],'set','viewport','390','844')
        mobile=evaluate("document.getElementById('mode-table').scrollIntoView();({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})")
        assert mobile['width']==390 and mobile['scrollWidth']<=390,mobile
        cmd('exec','screenshot','mobile-comparison.png');results.append({'case':'mobile-layout','result':mobile})
        cmd('exec','snapshot','-i')
    finally:
        if session:
            stop=cmd('stop');(proof/'stop.txt').write_text(stop)
            for name in ('Console','Server'):
                match=re.search(name+r' errors:\s+(\d+)',stop)
                errors[name.lower()]=int(match[1]) if match else None
        # Only the process group started above is owned by this verifier.
        try:os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        stream.close()
    assert errors=={'console':0,'server':0},errors
    write_json(out/'ui-verification.json',{'passed':True,'source_hash':production_code_hash(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'selected_variant':read_json(out/'acceptance.json')['selected_variant'],'errors':errors,
        'results':results,'actual_export':export_meta,'export_path':'ui/browser-comparison-export.json',
        'session_dir':str(Path(session['sessionDir']).relative_to(out)),'session_name':env['AGENT_BROWSER_SESSION'],
        'scope':'Actual local form requests, visible classifications and proof completeness, real export Blob, strict abstention, incomplete budget, cleared invalid input and 390px viewport. No publication.'})
    print('browser verification passed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--work',required=True);parser.add_argument('--port',type=int,default=18769)
    args=parser.parse_args();run(args.out,args.work,args.port)
