"""Executed architecture gates and source-bound unchanged legal recognition."""
import argparse
import ast
import builtins
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from pln_chess.common import ROOT,canonical,digest,read_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.pln import Runtime
from pln_chess.cycle14.model import PreferenceModel
from pln_chess.cycle14.ontology import key
from evaluation.cycle3 import read_gzip
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def boundary(out):
    out=Path(out);runtime=Runtime(timeout=900);runtime.verify();code=production_code_hash()
    assert code==read_json(out/'source-freeze.json')['production_code_hash']
    imports=[];arithmetic=[];operators=set()
    for path in sorted((ROOT/'src/pln_chess').rglob('*.py')):
        source=path.read_text();tree=ast.parse(source)
        for node in ast.walk(tree):
            modules=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            if path!=ROOT/'src/pln_chess/cli/__init__.py':
                imports.extend(dict(path=str(path.relative_to(ROOT)),module=name,line=node.lineno)
                    for name in modules if name.split('.')[0] in ('chess','training','evaluation'))
            if 'cycle14' in path.parts and isinstance(node,ast.BinOp) and any(
                isinstance(t,ast.Attribute) and t.attr in ('strength','confidence') or
                isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value in ('strength','confidence') for t in ast.walk(node)):
                arithmetic.append(dict(path=str(path.relative_to(ROOT)),line=node.lineno,expression=ast.unparse(node)))
        if 'cycle14' in path.parts:operators.update(re.findall(r'\((Truth_[A-Za-z0-9_]+|BestConfidenceCandidate)\b',source))
    allowed=set(read_json(ROOT/'configs/cycle13.json')['native_operators']);assert not imports and not arithmetic and operators<=allowed
    start=read_json(ROOT/'configs/cycle14.json')['starting_head']
    previous=set(subprocess.check_output(['git','ls-tree','-r','--name-only',start,'--','src'],text=True).splitlines())
    changed=set(subprocess.check_output(['git','diff','--name-only',start,'--','src'],text=True).splitlines())
    permitted={'src/pln_chess/api/__init__.py','src/pln_chess/cli/__init__.py','src/pln_chess/cli/web.py','src/pln_chess/cycle13/acceptance.py'}
    assert changed&previous<=permitted
    protected=read_json(out/'baseline/manifest.json')['protected_files'];changes=[p for p,h in protected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h];assert not changes
    inventory={};training=[]
    for path in sorted((out/'model').glob('*.json')):
        if path.name=='registry.json' or read_json(path).get('schema')!='relative-preference-model-v14':continue
        model=PreferenceModel.load(path,runtime)
        for identifier,h in model.hypotheses.items():
            assert key(h['descriptor'])==identifier
            assert not re.search(r'"[a-h][1-8]"',canonical(h['descriptor']))
        inventory[path.name]=dict(version=model.version,abstraction=model.abstraction,hypotheses=len(model.hypotheses),
            descriptors={k:h['descriptor'] for k,h in model.hypotheses.items()},concepts=model.use_concepts)
    for path in sorted(out.glob('learning/*/native-training.json.xz')):
        traces=read_gzip(path)['traces'];values=runtime.batch([(n['id'],n['native_expression']) for n in traces])
        assert all(values[n['id']].json()==n['truth_value'] for n in traces)
        training.append(dict(path=str(path.relative_to(out)),sha256=sha(path),nodes=len(traces),exact=True))
    traces={}
    for path in sorted(out.glob('evaluation/*/native-predictions.json.xz')):
        for row in read_gzip(path):
            result=row['prediction'];trace=result['proof_trace'];assert result['proof_id']==digest(trace)
            if trace:traces.setdefault(result['proof_id'],trace)
    for trace in traces.values():
        values=runtime.batch([(n['id'],n['native_expression']) for n in trace]);assert all(values[n['id']].json()==n['truth_value'] for n in trace)
    probe='''import builtins,json,os,sys
original=builtins.__import__
def guarded(name,*args,**kwargs):
 if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('Production oracle import: '+name)
 return original(name,*args,**kwargs)
builtins.__import__=guarded
from pln_chess.cycle14.inspector import inspect
from pln_chess.cycle14.proofs import ProofStore
with ProofStore() as store:
 result=inspect(dict(fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',move_a='a1a2',move_b='a1b1',preference_model='primary-immediate',max_candidates=2),store=store)
 assert not result['execution']['truncated'] and result['automatic_move_selection'] is False
 print(json.dumps(dict(passed=True,status=result['preference']['status'],model_versions=result['model_versions'],oracle_modules=[n for n in sys.modules if n.split('.')[0] in ('chess','training','evaluation')])))'''
    isolated=json.loads(subprocess.check_output([sys.executable,'-c',probe],cwd=ROOT,env=dict(os.environ,C14_OUT=str(out),TMPDIR='/dev/shm'),text=True));assert not isolated['oracle_modules']
    legal_probe='''import builtins,json,sys
original=builtins.__import__
def guarded(name,*args,**kwargs):
 if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError(name)
 if name.startswith(('pln_chess.cycle11.fields','pln_chess.cycle12','pln_chess.cycle13','pln_chess.cycle14')) and not name.endswith('.acceptance'):raise AssertionError(name)
 return original(name,*args,**kwargs)
builtins.__import__=guarded
from pln_chess.common import ROOT
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.api import explain_move
r=Runtime();m=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',r)
x=explain_move('7k/8/8/8/R6p/8/8/6K1 w - - 0 1','a4h4',m,runtime=r,mode='operational')
assert x['candidate']['classification']=='supported-legal'
print(json.dumps(dict(passed=True,classification=x['candidate']['classification'],model_version=m.version)))'''
    legal=json.loads(subprocess.check_output([sys.executable,'-c',legal_probe],cwd=ROOT,text=True))
    atomic_json(out/'architecture/boundary.json',dict(passed=True,production_code_hash=code,runtime=runtime.manifest,
        production_oracle_imports=imports,host_truth_value_arithmetic=arithmetic,observed_operators=sorted(operators),allowed_operators=sorted(allowed),
        unchanged_historical_files=len(protected),historical_changes=changes,changed_historical_source=sorted(changed&previous),
        operational_inference_core_unchanged=True,trained_descriptors=inventory,native_training_replay=training,
        distinct_final_native_proofs_replayed=len(traces),oracle_disabled_compact_inference=isolated,isolated_legal_inference=legal,
        preferences_promoted=False,automatic_selection=False,native_resident_persistent_reasoning_graph=False,
        scope='Executed import guards, AST boundary checks, every primary training/final preference trace reexecution, and historical byte hashes; not a formal proof of every possible information flow.'))


def acceptance(out):
    from pln_chess.cycle14.acceptance import CHECKS
    from pln_chess.learning import Model
    out=Path(out);code=production_code_hash();runtime=Runtime();cfg=read_json(ROOT/'configs/cycle14.json')
    mapping=dict(baseline='baseline/reproduction-receipt.json',current_native_parity='current/verified.json',
        negative_controls='current/verified.json',tests='current/verified.json',clean_bootstrap='clean-research/bootstrap/verified.json',
        native_boundary='architecture/boundary.json',preference_isolation='architecture/boundary.json',cache_parity='performance/summary.json',
        concept_preservation='preservation/concepts.json',dataset_integrity='datasets/integrity.json',artifact_preservation='architecture/boundary.json',
        api_compatibility='interfaces/verified.json',temporal_robustness='temporal/summary.json',research_reproduction='clean-research/verified.json',
        evidence_replay='dependence/summary.json',compact_integrity='clean-research/proof-replay/verified.json',
        reference_audit='reference-audit/resolution-census.json',relative_representation='representation/locality-summary.json')
    assert set(mapping)==set(CHECKS)
    gates={name:read_json(out/path) for name,path in mapping.items()};assert all(g['passed'] for g in gates.values())
    current=gates['current_native_parity'];assert current['identity']['production_code_hash']==code
    assert (current['legal_shards'],current['legal_rows'],current['negative_controls'],current['history_controls'],current['recoveries'],current['holdouts'])==(206,584112,287,27,2,76)
    assert current['exact_native_proof_parity'] and current['classification_changes']==0
    assert not any(current[k] for k in ('new_false_legal','new_false_illegal','new_self_check_false_legal'))
    assert current['test_count']>=588
    assert gates['clean_bootstrap']['identity']['production_code_hash']==code
    for name in ('native_boundary','cache_parity','api_compatibility','research_reproduction','compact_integrity'):
        assert gates[name]['production_code_hash']==code,name
    assert all(r['exact'] for r in gates['cache_parity']['parity'].values())
    assert gates['compact_integrity']['archives']==1180
    model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',runtime);assert model.version==cfg['accepted_legal_model_version']
    (out/'model').mkdir(exist_ok=True);shutil.copy2(ROOT/'artifacts/cycle12/model/C12-default.json',out/'model/C14-default.json')
    atomic_json(out/'acceptance.json',dict(passed=True,all_required_checks_executed=True,checks={name:True for name in CHECKS},
        gate_receipts={name:dict(path=path,sha256=sha(out/path)) for name,path in mapping.items()},
        default_model_version=model.version,accepted_model_versions=[model.version],
        accepted_legacy_model_versions=read_json(ROOT/'artifacts/cycle12/acceptance.json')['accepted_legacy_model_versions'],
        preference_model_is_default=False,new_legal_learning_promoted=False,runtime_version=runtime.version,
        production_code_hash=code,registration_hash=digest(cfg),legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in range(6,14)},
        accepted_legal_checkpoint_sha256=sha(out/'model/C14-default.json'),
        scope='Source-bound recognition of the unchanged legal checkpoint after complete engineering gates; experimental preference outcomes do not change defaults.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('boundary','acceptance'));p.add_argument('--out',default='artifacts/cycle14');a=p.parse_args();globals()[a.action](a.out)
