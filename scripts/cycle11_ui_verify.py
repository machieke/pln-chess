"""ProofShot browser workflow for the independent relational field inspector."""
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

from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash


def run(out, work, port=18781):
    out, work = Path(out).resolve(), Path(work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    assert read_json(out / 'acceptance.json')['passed']
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(('127.0.0.1', port))
    proof = out / 'ui'
    proof.mkdir(exist_ok=True)
    write_json(work / 'proofshot.config.json', dict(output=str(proof), viewport=dict(width=1280, height=900)))
    env = dict(os.environ, C11_OUT=str(out), TMPDIR='/dev/shm', AGENT_BROWSER_SESSION='pln-chess-cycle11-'+uuid.uuid4().hex[:12])
    for key in ('C6_OUT', 'C7_OUT', 'C8_OUT', 'C9_OUT', 'C10_OUT'):
        env.pop(key, None)
    commands, checks = [], []

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
            command('exec', '--session', env['AGENT_BROWSER_SESSION'], 'set', 'viewport', str(width), str(height))
            actual = evaluate(f'(async()=>{{const end=Date.now()+5000;while((innerWidth!=={width}||innerHeight!=={height})&&Date.now()<end)await new Promise(r=>setTimeout(r,100));return [innerWidth,innerHeight]}})()')
            if actual == [width, height]:
                return
        raise AssertionError(actual)

    def submit(example=None, **fields):
        script = '(async()=>{const example='+json.dumps(example)+';if(example){const e=document.getElementById("field-example");e.value=example;e.dispatchEvent(new Event("change"));}'
        script += 'for(const [id,value] of Object.entries('+json.dumps(fields)+')){document.getElementById(id).value=value;}'
        script += 'document.getElementById("field-form").requestSubmit();while(document.getElementById("field-run").disabled)await new Promise(r=>setTimeout(r,100));return {status:document.getElementById("field-status").textContent,candidate:document.getElementById("field-candidate-status").textContent,rows:document.querySelectorAll("#field-relations tbody tr").length,before:document.querySelectorAll("#field-before .cell").length,after:document.querySelectorAll("#field-after .cell").length};})()'
        result = evaluate(script)
        assert not result['status'].startswith('Error:'), result
        return result

    argv = [sys.executable, '-m', 'pln_chess', 'serve', '--checkpoint', str(ROOT / 'artifacts/cycle10/model/C10-default.json'), '--port', str(port)]
    token = uuid.uuid4().hex
    owner = work / 'owned-server.json'
    wrapper = work / 'owned-server.py'
    wrapper.write_text('import json,os\nfrom pathlib import Path\n'+f'Path({str(owner)!r}).write_text(json.dumps({{"pid":os.getpid(),"pgid":os.getpgrp(),"token":{token!r}}}))\n'+f'os.execv({sys.executable!r},{argv!r})\n')
    stream = (proof / 'launcher.txt').open('w')
    launch = subprocess.Popen(['proofshot', 'start', '--run', 'exec '+shlex.join([sys.executable, str(wrapper)]),
        '--port', str(port), '--description', 'Cycle 11 field selection, hypothetical successors, typed differences, native proofs, unknowns, exports and desktop/mobile layouts'],
        cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    session, errors, cleanup, export = None, {}, {}, None
    try:
        end = time.time()+60
        while not (proof / '.session.json').exists():
            if launch.poll() is not None or time.time() > end:
                raise RuntimeError('ProofShot startup failed')
            time.sleep(.2)
        session = read_json(proof / '.session.json')
        command('exec', 'open', f'http://127.0.0.1:{port}/fields')
        viewport(1280, 900)
        snapshot = command('exec', 'snapshot', '-i')
        assert 'Build fields' in snapshot
        command('exec', 'screenshot', 'initial-fields.png')
        cases = read_json(out / 'datasets/worked-controls.json')['worked']
        for case in cases:
            result = submit(case['id'])
            assert result['rows'] > 0 and result['before'] == result['after'] == 64
            checks.append(dict(case=case['id'], result=result))
            if case['id'] in ('rook-obstruction', 'pinned-defender', 'unknown-observation', 'promotion', 'en-passant-exposure'):
                command('exec', 'screenshot', case['id']+'.png')
        submit('rook-obstruction')
        for family in ('attack', 'defense', 'mobility', 'king-exposure'):
            result = submit(**{'field-family': family})
            checks.append(dict(case='family-'+family, result=result))
        submit('rook-obstruction', **{'field-family':'attack'})
        inspected = evaluate('(async()=>{const b=document.querySelector("#field-relations button");b.click();const p=document.getElementById("field-proof");const d=JSON.parse(p.textContent);return {proof:d.proof_id,nodes:d.proof_trace.length,rule:d.rule_id,evidence:d.evidence_ids.length,classification:d.classification};})()')
        assert inspected['proof'] and inspected['rule']
        checks.append(dict(case='native-proof-inspection', result=inspected))
        evaluate('document.getElementById("field-proof").scrollIntoView();true')
        command('exec', 'screenshot', 'native-field-proof.png')
        empty = submit('rook-obstruction', **{'field-model':'empty'})
        assert evaluate('Array.from(document.querySelectorAll("#field-relations tbody tr")).every(r=>r.textContent.includes("unknown"))')
        checks.append(dict(case='empty-checkpoint-abstains', result=empty))
        incomplete = submit(**{'field-model':'trained', 'field-budget':0})
        assert 'incomplete' in evaluate('document.getElementById("field-relations").textContent')
        checks.append(dict(case='native-budget-incomplete', result=incomplete))
        submit('en-passant', **{'field-budget':100000})
        export = evaluate('(async()=>{const old=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{window.fieldBlob=b;return old(b)};document.getElementById("field-export").click();window.fieldText=await window.fieldBlob.text();const bytes=new TextEncoder().encode(window.fieldText);const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))).map(x=>x.toString(16).padStart(2,"0")).join("");return {bytes:bytes.length,characters:window.fieldText.length,sha256:hash};})()')
        raw = ''.join(evaluate(f'window.fieldText.slice({i},{i+100000})') for i in range(0, export['characters'], 100000)).encode()
        assert hashlib.sha256(raw).hexdigest() == export['sha256']
        decoded = json.loads(raw)
        assert decoded['before']['relations'] and decoded['after']['relations']
        assert all(c['change_truth_value'] is None for c in decoded['differences'])
        (proof / 'browser-field-export.json').write_bytes(raw)
        checks.append(dict(case='actual-before-after-native-proof-export', result=export))
        viewport(390, 844)
        evaluate('window.scrollTo(0,0);true')
        mobile = evaluate('({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})')
        assert mobile['width'] == 390 and mobile['scrollWidth'] <= 390
        command('exec', 'screenshot', 'mobile-field-controls.png')
        evaluate('document.getElementById("field-before").scrollIntoView();true')
        command('exec', 'screenshot', 'mobile-before-after.png')
        checks.append(dict(case='mobile-layout', result=mobile))
        command('exec', 'open', f'http://127.0.0.1:{port}')
        legacy = command('exec', 'snapshot', '-i', '-s', '#form')
        assert 'Explain' in legacy or 'Run' in legacy
        checks.append(dict(case='existing-legal-inspector-controls-present'))
    finally:
        try:
            if session:
                stopped = command('stop')
                (proof / 'stop.txt').write_text(stopped)
                for kind in ('Console', 'Server'):
                    match = re.search(kind+r' errors:\s+(\d+)', stopped)
                    errors[kind.lower()] = int(match[1]) if match else None
        finally:
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
    assert errors == dict(console=0, server=0), errors
    write_json(proof / 'verification.json', dict(passed=True, source_hash=production_code_hash(), checks=checks,
        errors=errors, actual_export=export, server_cleanup=cleanup,
        session_dir=str(Path(session['sessionDir']).relative_to(out))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--work', required=True)
    parser.add_argument('--port', type=int, default=18781)
    args = parser.parse_args()
    run(args.out, args.work, args.port)
