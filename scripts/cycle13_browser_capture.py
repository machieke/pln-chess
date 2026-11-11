"""Capture compact facts from the recorded browser, including original response bytes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from pln_chess.common import ROOT,write_json

EXPRESSION=r'''(async()=>{
 const r=window.plnPreferenceResult;
 if(!r||document.getElementById('compare').disabled)throw Error('No completed inspection');
 const raw=new TextEncoder().encode(window.plnPreferenceResultRaw);
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw))).map(v=>v.toString(16).padStart(2,'0')).join('');
 const preferences=r.comparisons||[{preference:r.preference}];
 const legalCandidates=Object.fromEntries(await Promise.all(Object.entries(r.legality||r.immediate.legality).map(async([side,candidate])=>{
  const bytes=new TextEncoder().encode(JSON.stringify(candidate));
  const value=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(v=>v.toString(16).padStart(2,'0')).join('');
  return [side,{move:candidate.move,classification:candidate.classification,proof_nodes:candidate.proof_trace.length,
   raw_stv:candidate.raw_stv,legal_move_truth_value:candidate.legal_move_truth_value,
   evidence_ids:[...candidate.evidence_ids].sort(),
   browser_json_sha256:value,scope:'Hash of the complete browser-parsed legal candidate, including its ordered native proof. This is not a model-supplied proof ID.'}];
 })));
 return JSON.stringify({url:location.href,sourceIndex:document.getElementById('example').value,
  fen:r.fen,moves:r.moves,model:r.inspector_model,models:r.model_versions,runtime:r.runtime_version,
  statusText:document.getElementById('status').textContent,verdict:document.getElementById('verdict').textContent,
  preferences:preferences.map(p=>({horizon:p.horizon,status:p.preference.status,channels:p.preference.channels,
   proofId:p.preference.proof_id,nativeNodes:p.preference.proof_trace.length,evidenceIds:p.preference.evidence_ids,
   conditionalComplete:p.preference.conditional_proof_complete,jointComplete:p.preference.joint_proof_complete})),
  legalCandidates,
  stateNames:Object.keys(r.states),selectedState:document.getElementById('state').value,
  boardCells:[document.querySelectorAll('#before-board .cell').length,document.querySelectorAll('#after-board .cell').length],
  width:innerWidth,documentWidth:document.documentElement.scrollWidth,noHorizontalOverflow:document.documentElement.scrollWidth<=innerWidth,
  proofPage:document.getElementById('proof-page').textContent,execution:r.execution,
  rawBytes:raw.length,rawSha256:hash,unexaminedResponses:r.unexamined_responses||null});
})()'''


def run(name,session,out):
    env=dict(os.environ,AGENT_BROWSER_SESSION=session,TMPDIR='/dev/shm')
    process=subprocess.run(['proofshot','exec','eval',EXPRESSION],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if process.returncode:
        target=Path(out)/'ui/capture-errors'/(name+'.txt');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(process.stdout)
        raise RuntimeError('Browser capture failed; retained diagnostics at '+str(target))
    output=process.stdout
    value=json.loads(output)
    if isinstance(value,str):value=json.loads(value)
    assert value['boardCells']==[64,64] and value['noHorizontalOverflow']
    assert not value['execution']['truncated']
    assert set(value['legalCandidates'])=={'A','B'}
    assert all(candidate['proof_nodes']>0 for candidate in value['legalCandidates'].values())
    write_json(Path(out)/'ui/observations'/(name+'.json'),value)
    print(json.dumps({k:value[k] for k in ('verdict','width','selectedState','rawBytes','rawSha256')},sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--session',default='pln-cycle13-final')
    parser.add_argument('--out',default='artifacts/cycle13');args=parser.parse_args();run(args.name,args.session,args.out)
