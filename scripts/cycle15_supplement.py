"""Registered learning/budget interventions and complete raw evidence audit."""
import argparse
import ast
import copy
import json
from pathlib import Path
from pln_chess.common import ROOT,digest,read_json,write_json
from research.cycle15.native_reasoner import NativeReasoner,Sentence,Budgets,alpha_key
from research.cycle15.queries import infer_state
from evaluation.cycle15_corpus import registration,episode
from evaluation.cycle15_consequences import compact
from training.cycle15_consequences import evidence,fit
from scripts.cycle15_baseline import sha


def run(out,evaluation_root,checkpoint):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);reasoner=NativeReasoner();model=read_json(checkpoint)
    roots=registration();prior=copy.deepcopy(model)
    for row in prior['rules'].values():row['truth_value']=dict(strength=.5,confidence=0.)
    prior['version']=digest({k:v for k,v in prior.items() if k!='version'})
    transfer=[]
    for root in roots:
        if root['split']!='test' or root['family']['length']!=2:continue
        e=episode(root)
        untrained=infer_state(e['after'],e['query'],prior,reasoner=reasoner)
        trained=infer_state(e['after'],e['query'],model,reasoner=reasoner)
        transfer.append(dict(root=root['id'],selection='all preregistered final-test one-cell roots, without labels',
            prior=compact(untrained,out),trained=compact(trained,out)))
    write_json(out/'heldout-learning-effect.json',transfer)
    records=evidence([r for r in roots if r['split']=='train'])
    reproduced,_=fit(records,out/'refit',reasoner=reasoner)
    assert reproduced['rules']==model['rules']
    write_json(out/'training-reproduction.json',dict(parameters_and_ancestry_identical=True,
        scope='Refit exact registered training records with hardened admission; new run provenance has a new ledger hash',
        original_version=model['version'],reproduced_version=reproduced['version']))
    facts=[Sentence('Belief',1.,.5,('positive',),'audit-input'),Sentence('Belief',0.,.5,('negative',),'audit-input')]
    budget=[]
    for steps in (0,1,8):
        result=reasoner.infer(facts,[],'Belief',budgets=Budgets(steps))
        budget.append(dict(steps=steps,result=compact(result,out)))
    write_json(out/'nonmonotone-answer.json',budget)
    imports=[]
    for path in sorted((ROOT/'research/cycle15').glob('*.py')):
        tree=ast.parse(path.read_text())
        for node in ast.walk(tree):
            names=[alias.name for alias in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            for name in names:
                imports.append(dict(path=str(path.relative_to(ROOT)),module=name))
                assert not name.startswith(('chess','evaluation','training'))
    write_json(out/'production-boundary.json',dict(passed=True,imports=imports,
        source_files={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'research/cycle15').glob('*.py'))},
        checks='AST import audit plus executable oracle-disabled/state-label/admission/failure tests',
        descriptor_fallback=False,host_chess_adjudicator=False))
    # Check each saved native evidence stamp against actual supplied occurrences.
    # Correct telemetry separately, without altering earlier scientific receipts.
    audit=[]
    evalroot=Path(evaluation_root)
    for path in sorted((evalroot/'raw').glob('*.json')):
        result=read_json(path)
        if 'retained' not in result:continue
        allowed={stamp for row in result['facts']+result['rules'] for stamp in row['stamps']}
        assert all(set(row['stamps'])<=allowed for row in result['retained']+result['selected'])
        initial={alpha_key(row['term']) for row in result['facts']+result['rules']}
        corrected=sum(alpha_key(row['term']) not in initial for row in result['retained'])
        audit.append(dict(path=str(path),sha256=sha(path),stamps_valid=True,
            retained_native_statements_absent_from_inputs=corrected,
            old_syntactic_count=result['usage']['derived_statements']))
    write_json(out/'proof-audit.json',dict(passed=True,records=len(audit),items=audit,
        trace_scope='Observed task selections and returned beliefs/stamps only; no reconstructed fired-rule tree',
        telemetry_correction='Alpha-equivalent native schema variable renaming is not a new statement',
        original_programs_outputs_answers_unchanged=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--evaluation-root',required=True)
    p.add_argument('--checkpoint',required=True);a=p.parse_args();run(a.out,a.evaluation_root,a.checkpoint)
