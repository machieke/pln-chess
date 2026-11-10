"""ProofShot browser workflow for the independent relational field inspector."""
import argparse
import base64
import gzip
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

from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash


def run(out, work, port=18782, development=False):
    out, work = Path(out).resolve(), Path(work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    if not development:
        assert read_json(out / 'acceptance.json')['passed']
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(('127.0.0.1', port))
    proof = out / ('ui-development' if development else 'ui')
    proof.mkdir(exist_ok=True)
    write_json(work / 'proofshot.config.json', dict(output=str(proof), viewport=dict(width=1280, height=900)))
    env = dict(os.environ, C12_OUT=str(out), TMPDIR='/dev/shm', AGENT_BROWSER_SESSION='pln-chess-cycle12-'+uuid.uuid4().hex[:12])
    write_json(work/'browser-session.json',dict(session=env['AGENT_BROWSER_SESSION']))
    for key in ('C6_OUT', 'C7_OUT', 'C8_OUT', 'C9_OUT', 'C10_OUT', 'C11_OUT'):
        env.pop(key, None)
    commands, checks = [], []
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Browser verification interrupted by signal '+str(signum))
    signal.signal(signal.SIGTERM,interrupted)

    def owned_browser_pids():
        result=[]
        for line in subprocess.check_output(['ps','-eo','pid,args'],text=True).splitlines():
            parts=line.strip().split(None,1)
            if len(parts)!=2 or not parts[0].isdigit() or 'agent-browser-linux-x64' not in parts[1]:continue
            pid=int(parts[0])
            try:
                environment=Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
                if ('AGENT_BROWSER_SESSION='+env['AGENT_BROWSER_SESSION']).encode() in environment:result.append(pid)
            except (PermissionError,FileNotFoundError):pass
        return result

    def command(*args, structured=False):
        started = time.time()
        result = subprocess.run(['proofshot', *args], cwd=work, env=env, capture_output=True, text=True, timeout=60)
        commands.append(dict(args=list(args), returncode=result.returncode, seconds=time.time()-started,
            stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(), stderr=result.stderr))
        write_json(proof / 'commands.json', commands)
        if result.returncode:
            raise RuntimeError((args, result.stderr, result.stdout[:1500]))
        return json.loads(result.stdout) if structured else result.stdout

    def evaluate(script):
        return command('exec', 'eval', script, structured=True)

    def viewport(width, height):
        for _ in range(3):
            command('exec', 'set', 'viewport', str(width), str(height))
            actual = evaluate(f'(async()=>{{const end=Date.now()+5000;while((innerWidth!=={width}||innerHeight!=={height})&&Date.now()<end)await new Promise(r=>setTimeout(r,100));return [innerWidth,innerHeight]}})()')
            if actual == [width, height]:
                return
        raise AssertionError(actual)


    def submit(mode=None, example=None, **fields):
        script = '(async()=>{const mode='+json.dumps(mode)+';if(mode){const e=document.getElementById("view-mode");e.value=mode;e.dispatchEvent(new Event("change"));}'
        script += 'const example='+json.dumps(example)+';if(example!==null){const e=document.getElementById("example");e.value=String(example);e.dispatchEvent(new Event("change"));}'
        script += 'for(const [id,value] of Object.entries('+json.dumps(fields)+'))document.getElementById(id).value=value;'
        script += 'document.getElementById("inspect-form").requestSubmit();while(document.getElementById("run").disabled)await new Promise(r=>setTimeout(r,100));return {status:document.getElementById("status").textContent,transition:document.getElementById("transition").textContent,rows:document.querySelectorAll("#relations tbody tr").length,before:document.querySelectorAll("#before .cell").length,after:document.querySelectorAll("#after .cell").length,concepts:document.querySelectorAll(".concept-card").length,edges:document.querySelectorAll("#graph g").length};})()'
        result=evaluate(script)
        assert not result['status'].startswith('Error:'), result
        return result

    checkpoint=ROOT/'artifacts/cycle10/model/C10-default.json' if development else out/'model/C12-default.json'
    argv = [sys.executable, '-m', 'pln_chess', 'serve', '--checkpoint', str(checkpoint), '--port', str(port)]
    token = uuid.uuid4().hex
    owner = work / 'owned-server.json'
    wrapper = work / 'owned-server.py'
    wrapper.write_text('import json,os\nfrom pathlib import Path\n'+f'Path({str(owner)!r}).write_text(json.dumps({{"pid":os.getpid(),"pgid":os.getpgrp(),"token":{token!r}}}))\n'+f'os.execv({sys.executable!r},{argv!r})\n')
    stream = (proof / 'launcher.txt').open('w')
    launch = subprocess.Popen(['proofshot', 'start', '--run', 'exec '+shlex.join([sys.executable, str(wrapper)]),
        '--port', str(port), '--description', 'Cycle 12 concept selection, dependency graph, supplied sequence steps, gaps, native proofs, exports and desktop/mobile layouts'],
        cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    session, errors, cleanup, export = None, {}, {}, None
    browser_pids=[]
    try:
        end = time.time()+60
        while not (proof / '.session.json').exists():
            if launch.poll() is not None or time.time() > end:
                raise RuntimeError('ProofShot startup failed')
            time.sleep(.2)
        session = read_json(proof / '.session.json')
        browser_pids=owned_browser_pids()
        command('exec', 'open', f'http://127.0.0.1:{port}/interactions')
        viewport(1280, 900)
        snapshot = command('exec', 'snapshot', '-i')
        assert 'Inspect evidence' in snapshot
        command('exec', 'screenshot', 'initial-interactions.png')

        first=submit('snapshot',0)
        assert first['rows'] and first['edges'] and first['before']==first['after']==64
        checks.append(dict(case='before-after-graph',result=first))
        command('exec','screenshot','before-after-interactions.png')
        for family in ('attack','defense','mobility','king-exposure'):
            result=submit(**{'family':family});checks.append(dict(case='family-'+family,result=result))
        # The catalog has eight inputs per concept, selected independently of model predictions.
        from pln_chess.cycle12.api import inspector_catalog
        catalog=inspector_catalog();first_by_concept={}
        for i,case in enumerate(catalog['concept_examples']):first_by_concept.setdefault(case['concept'],i)
        for concept,index in first_by_concept.items():
            result=submit('concept',index,**{'family':'all','piece':''})
            assert result['concepts']==1
            checks.append(dict(case='concept-'+concept,result=result))
        evaluate('document.getElementById("concepts").scrollIntoView();true')
        command('exec','screenshot','partial-concept-and-gaps.png')
        evaluate('document.getElementById("graph").scrollIntoView();true')
        command('exec','screenshot','dependency-graph.png')
        evaluate('document.querySelector("#graph g").dispatchEvent(new Event("click"));true')
        edge=evaluate('JSON.parse(document.getElementById("proof").textContent)')
        assert edge['edge']['origin'] in ('native','host-scheduling','host-projection','host-comparison')
        checks.append(dict(case='graph-provenance-inspection',origin=edge['edge']['origin']))
        submit('snapshot',0,**{'family':'attack','piece':'a4','concept':'all'})
        inspected=evaluate('(async()=>{const b=document.querySelector("#relations button[data-native="+JSON.stringify("true")+"]");b.click();const d=JSON.parse(document.getElementById("proof").textContent);return {proof:d.proof_id,nodes:d.proof_trace.length,rule:d.rule_id,evidence:d.evidence_ids.length};})()')
        assert inspected['nodes'] and inspected['rule'] and inspected['evidence']
        checks.append(dict(case='native-proof-inspection',result=inspected))
        evaluate('document.getElementById("proof").scrollIntoView();true')
        command('exec','screenshot','native-proof.png')
        empty=submit(**{'field-model':'empty','concept-model':'empty'})
        assert evaluate('Array.from(document.querySelectorAll("#relations tbody tr")).every(r=>r.textContent.includes("unknown"))')
        checks.append(dict(case='empty-evidence-abstains',result=empty))
        incomplete=submit(**{'field-model':'trained','concept-model':'trained','budget':0})
        assert 'Incomplete' in incomplete['status'];checks.append(dict(case='zero-budget',result=incomplete))
        unknown=submit(**{'budget':100000,'unknown':'a4'})
        assert evaluate('Array.from(document.querySelectorAll("#relations tbody tr")).every(r=>r.textContent.includes("unknown"))')
        checks.append(dict(case='unknown-source',result=unknown))
        sequence_index=next(i for i,s in enumerate(catalog['sequences']) if s['id']=='promotion-threat')
        sequence=submit('sequence',sequence_index,**{'family':'attack','unknown':'','candidate-limit':4})
        assert 'complete supplied history' in sequence['transition']
        for step in range(5):
            result=evaluate(f'document.getElementById("step").value={step};document.getElementById("step").dispatchEvent(new Event("input"));({{label:document.getElementById("step-label").textContent,transition:document.getElementById("transition").textContent}})')
            assert result['label'].startswith('S'+str(step)+' ');checks.append(dict(case='sequence-step-'+str(step),result=result))
        evaluate('document.getElementById("step").scrollIntoView();true')
        command('exec','screenshot','supplied-sequence-promotion.png')
        partial=dict(catalog['sequences'][sequence_index]);partial=json.loads(json.dumps(partial));partial['events'][1]['move']=None
        result=submit(**{'supplied':json.dumps(partial)})
        evaluate('document.getElementById("step").value=2;document.getElementById("step").dispatchEvent(new Event("input"));true')
        assert 'missing-event-observed-state' in evaluate('document.getElementById("transition").textContent')
        checks.append(dict(case='missing-event-gap',result=result))
        command('exec','screenshot','missing-event-gap.png')
        # Capture a compact actual native package through the browser export event.
        submit('snapshot',0,**{'family':'attack','piece':'a4','candidate-limit':0,'unknown':''})
        export=evaluate('(async()=>{const old=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.proofBlob=b;return old(b)};document.getElementById("export").click();const text=await window.proofBlob.text();const bytes=new TextEncoder().encode(text);const packed=new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer());let binary="";for(let i=0;i<packed.length;i+=32768)binary+=String.fromCharCode(...packed.subarray(i,i+32768));return {bytes:bytes.length,sha256:Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))).map(x=>x.toString(16).padStart(2,"0")).join(""),base64:btoa(binary),matchesServerResult:text===JSON.stringify(result,null,2)};})()')
        raw=gzip.decompress(base64.b64decode(export.pop('base64')))
        assert export['matchesServerResult']
        assert hashlib.sha256(raw).hexdigest()==export['sha256'];decoded=json.loads(raw)
        assert decoded['before']['relations'] and decoded['after']['relations'] and decoded['graph']['proofs']
        assert all(c['truth_value'] is None for c in decoded['changes'])
        from evaluation.cycle7_io import pack
        pack(proof/'browser-proof-export.json.xz',decoded)
        checks.append(dict(case='actual-native-graph-export',result=export))
        viewport(390,844);evaluate('window.scrollTo(0,0);true')
        mobile=evaluate('({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})')
        write_json(proof/'mobile-geometry.json',mobile)
        assert mobile['width']==390 and mobile['scrollWidth']<=390,mobile
        command('exec','screenshot','mobile-controls.png')
        evaluate('document.getElementById("before").scrollIntoView();true');command('exec','screenshot','mobile-boards.png')
        evaluate('document.getElementById("graph").scrollIntoView();true');command('exec','screenshot','mobile-graph.png')
        checks.append(dict(case='mobile-layout',result=mobile))
        command('exec','open',f'http://127.0.0.1:{port}/fields')
        assert 'Build fields' in command('exec','snapshot','-i');checks.append(dict(case='cycle11-inspector-preserved'))
        command('exec','open',f'http://127.0.0.1:{port}')
        assert 'Run' in command('exec','snapshot','-i','-s','#form');checks.append(dict(case='legal-inspector-preserved'))
    finally:
        try:
            if session:
                stopped = command('stop')
                (proof / 'stop.txt').write_text(stopped)
                for kind in ('Console', 'Server'):
                    match = re.search(kind+r' errors:\s+(\d+)', stopped)
                    errors[kind.lower()] = int(match[1]) if match else None
        finally:
            # A failed browser close may leave the owned recorder daemon alive.
            # Verify the unique session nonce again before stopping its group.
            for pid in browser_pids:
                if pid in owned_browser_pids():
                    try:
                        if os.getpgid(pid)==pid:os.killpg(pid,signal.SIGTERM)
                    except ProcessLookupError:pass
            if owner.exists():
                owned = read_json(owner)
                assert owned['token'] == token
                cleanup = dict(pid=owned['pid'], pgid=owned['pgid'], ownership_token_matched=True)
                try:
                    actual = Path(f"/proc/{owned['pid']}/cmdline").read_bytes().rstrip(b'\0').split(b'\0')
                    assert actual == [a.encode() for a in argv] and os.getpgid(owned['pid']) == owned['pgid']
                    os.killpg(owned['pgid'], signal.SIGTERM)
                except (ProcessLookupError, FileNotFoundError):
                    pass
            try:
                os.killpg(launch.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            stream.close()
    end = time.time()+5
    while True:
        with socket.socket() as probe:
            probe.settimeout(.2)
            listening = probe.connect_ex(('127.0.0.1', port)) == 0
        if not listening:
            break
        assert time.time() < end, 'Owned verification server remained listening'
        time.sleep(.1)
    cleanup['port_closed'] = True
    cleanup['owned_browser_pids']=browser_pids
    cleanup['remaining_owned_browser_pids']=owned_browser_pids()
    assert not cleanup['remaining_owned_browser_pids'],cleanup
    assert errors == dict(console=0, server=0), errors
    write_json(proof / 'verification.json', dict(passed=True, development_only=development, source_hash=production_code_hash(), checks=checks,
        errors=errors, actual_export=export, server_cleanup=cleanup,
        session_dir=str(Path(session['sessionDir']).relative_to(out))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--work', required=True)
    parser.add_argument('--port', type=int, default=18782)
    parser.add_argument('--development', action='store_true')
    args = parser.parse_args()
    run(args.out, args.work, args.port, args.development)
