"""Executed native boundaries and source-bound preservation of the legal default."""
import argparse
import ast
import builtins
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from pln_chess.common import ROOT,canonical,digest,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.pln import Runtime
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip

START='b000898a0a1f46e556f161982f2c0e6d3944c322'


def boundary(out):
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.concepts import ForkModel
    from pln_chess.cycle13.ontology import GRAMMAR,ABSTRACTIONS,key
    from pln_chess.cycle13.inspector import inspect
    out=Path(out);runtime=Runtime(timeout=600);runtime.verify()
    code=production_code_hash();assert code==read_json(out/'source-freeze.json')['production_code_hash']
    imports=[];arithmetic=[];operators=set()
    for path in sorted((ROOT/'src/pln_chess').rglob('*.py')):
        source=path.read_text();tree=ast.parse(source)
        for node in ast.walk(tree):
            modules=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            if path!=ROOT/'src/pln_chess/cli/__init__.py':
                imports.extend(dict(path=str(path.relative_to(ROOT)),module=name,line=node.lineno)
                    for name in modules if name.split('.')[0] in ('chess','training','evaluation'))
            if 'cycle13' in path.parts and isinstance(node,ast.BinOp):
                if any((isinstance(t,ast.Attribute) and t.attr in ('strength','confidence')) or
                    (isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value in ('strength','confidence'))
                    for t in ast.walk(node)):
                    arithmetic.append(dict(path=str(path.relative_to(ROOT)),line=node.lineno,expression=ast.unparse(node)))
        if 'cycle13' in path.parts:
            operators.update(re.findall(r'\((Truth_[A-Za-z0-9_]+|BestConfidenceCandidate)\b',source))
    allowed=set(read_json(ROOT/'configs/cycle13.json')['native_operators'])
    assert not imports and not arithmetic and operators<=allowed
    previous=set(subprocess.check_output(['git','ls-tree','-r','--name-only',START,'--','src'],cwd=ROOT,text=True).splitlines())
    changed=set(subprocess.check_output(['git','diff','--name-only',START,'--','src'],cwd=ROOT,text=True).splitlines())
    permitted={'src/pln_chess/api/__init__.py','src/pln_chess/cli/__init__.py','src/pln_chess/cli/web.py','src/pln_chess/cycle12/acceptance.py'}
    assert changed&previous<=permitted
    protected=read_json(out/'baseline/manifest.json')['protected_files']
    assert all(sha(ROOT/path)==value for path,value in protected.items())
    descriptors={}
    for path in sorted((out/'learning').glob('*/checkpoint.json')):
        model=PreferenceModel.load(path,runtime)
        for identifier,h in model.hypotheses.items():
            assert key(h['descriptor'])==identifier
            assert not re.search(r'"[a-h][1-8]"',canonical(h['descriptor']))
        descriptors[str(path.relative_to(out))]=dict(model_version=model.version,abstraction=model.abstraction,
            hypotheses=len(model.hypotheses),descriptors={k:h['descriptor'] for k,h in model.hypotheses.items()})
    fork=ForkModel.load(out/'model/C13-fork-role.json',runtime)
    training=[]
    for path in sorted((out/'learning').glob('*/native-training.json.xz'))+[out/'forks/native-training.json.xz',out/'consistency/learning/native-training.json.xz']:
        rows=read_gzip(path)['traces']
        values=runtime.batch([(n['id'],n['native_expression']) for n in rows])
        assert all(values[n['id']].json()==n['truth_value'] for n in rows)
        training.append(dict(path=str(path.relative_to(out)),sha256=sha(path),native_nodes=len(rows),exact=True))
    traces={}
    for name in ('preferences/relational.json.xz','preferences/full.json.xz','temporal/preferences.json.xz'):
        for row in read_gzip(out/name):
            result=row['result']
            if result['conditional_proof_complete']:
                traces.setdefault(result['proof_id'],result['proof_trace'])
    sampled=sorted(traces)[:40];replayed=[]
    for identifier in sampled:
        trace=traces[identifier];assert digest(trace)==identifier
        values=runtime.batch([(n['id'],n['native_expression']) for n in trace])
        assert all(values[n['id']].json()==n['truth_value'] for n in trace)
        replayed.append(dict(proof_id=identifier,native_nodes=len(trace),exact=True))
    original=builtins.__import__
    def no_oracle(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):
            raise AssertionError('Production reference dependency: '+name)
        return original(name,*args,**kwargs)
    try:
        builtins.__import__=no_oracle
        result=inspect(dict(fen='4k3/8/8/3p4/8/8/8/R3K3 w - - 0 1',move_a='a1a5',move_b='a1a4'))
        assert not result['execution']['truncated']
    finally:
        builtins.__import__=original
    # A fresh interpreter prevents previously loaded experimental modules from
    # concealing a dependency in the operational import path.
    probe='''import builtins,json,sys
original=builtins.__import__
def guarded(name,*args,**kwargs):
 if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError(name)
 if name.startswith(('pln_chess.cycle11.fields','pln_chess.cycle12','pln_chess.cycle13')) and not name.endswith('.acceptance'):raise AssertionError(name)
 return original(name,*args,**kwargs)
builtins.__import__=guarded
from pln_chess.common import ROOT
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.api import explain_move
r=Runtime();m=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',r)
x=explain_move('7k/8/8/8/R6p/8/8/6K1 w - - 0 1','a4h4',m,runtime=r,mode='operational')
assert x['candidate']['classification']=='supported-legal'
assert not any(n.startswith('pln_chess.cycle13.') and n!='pln_chess.cycle13.acceptance' for n in sys.modules)
print(json.dumps(dict(passed=True,classification=x['candidate']['classification'],model_version=m.version,experimental_modules_loaded=False)))'''
    import json
    isolated=json.loads(subprocess.check_output([sys.executable,'-c',probe],cwd=ROOT,text=True))
    write_json(out/'ontology/manifest.json',dict(grammar=GRAMMAR,abstractions=ABSTRACTIONS,checkpoints=descriptors,
        fork_model_version=fork.version,fork_descriptors={k:h['descriptor'] for k,h in fork.hypotheses.items()},
        production_code_hash=code,absolute_rule_constants=False,host_truth_value_composition=False,
        source_files={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src/pln_chess/cycle13').glob('*.py'))}))
    write_json(out/'architecture/boundary.json',dict(passed=True,production_code_hash=code,runtime=runtime.manifest,
        production_oracle_imports=imports,host_truth_value_arithmetic=arithmetic,
        observed_new_module_operators=sorted(operators),allowed_operators=sorted(allowed),
        new_native_operators=False,upstream_modified=False,protected_files=len(protected),
        historical_source_changes=sorted(changed&previous),operational_inference_core_unchanged=True,
        native_training_replays=training,native_training_nodes=sum(r['native_nodes'] for r in training),
        native_preference_proof_replays=replayed,oracle_disabled_comparison=result['preference']['status'],
        isolated_legal_path=isolated,preferences_promoted=False,
        scope='Executed source guards, fresh-process import isolation, native trace reexecution and protected-file hashes. This is not a formal proof of every possible information flow.'))
    print('CYCLE 13 NATIVE BOUNDARY VERIFIED',flush=True)


def acceptance(out):
    from pln_chess.cycle13.acceptance import CHECKS
    from pln_chess.learning import Model
    out=Path(out);code=production_code_hash();config=read_json(ROOT/'configs/cycle13.json');runtime=Runtime()
    mapping=dict(baseline='baseline/reproduction-receipt.json',current_native_parity='current/verified.json',
        negative_controls='current/verified.json',tests='current/verified.json',clean_bootstrap='bootstrap/verified.json',
        native_boundary='architecture/boundary.json',preference_isolation='architecture/boundary.json',
        cache_parity='performance/summary.json',concept_preservation='concepts/summary.json',
        dataset_integrity='datasets/integrity.json',artifact_preservation='architecture/boundary.json',
        api_compatibility='cli-smoke/verified.json',temporal_robustness='temporal/summary.json',
        research_reproduction='clean-research/verified.json')
    assert set(mapping)==set(CHECKS)
    gates={name:read_json(out/path) for name,path in mapping.items()}
    assert all(gate['passed'] for gate in gates.values())
    current=gates['current_native_parity'];baseline=gates['baseline'];boundary=gates['native_boundary']
    assert current['identity']['production_code_hash']==boundary['production_code_hash']==code
    assert current['legal_shards']==baseline['legal_shards']==206 and current['legal_rows']==baseline['legal_rows']==584112
    assert current['negative_controls']==287 and current['history_controls']==27 and current['recoveries']==2 and current['holdouts']==76
    assert current['exact_native_proof_parity'] and current['classification_changes']==0
    assert not any(current[k] for k in ('new_false_legal','new_false_illegal','new_self_check_false_legal'))
    assert current['test_count']>=584
    assert gates['clean_bootstrap']['identity']['production_code_hash']==code
    assert gates['research_reproduction']['production_code_hash']==code
    assert gates['api_compatibility']['production_code_hash']==code
    assert gates['cache_parity']['production_code_hash']==code
    assert all(row['exact'] for row in gates['cache_parity']['parity'].values())
    assert gates['concept_preservation']['all_previous_correct_preserved'] and gates['concept_preservation']['starting_native_proofs_unchanged']==370
    assert gates['temporal_robustness']['demonstrations']=={'2':10,'3':10}
    for path in (out/'current/legal/evaluation').glob('*.receipt.json'):
        receipt=read_json(path)
        assert receipt['passed'] and receipt['native_proofs_verified'] and receipt['identity']['production_code_hash']==code
        assert sha(out/'current'/receipt['artifact'])==receipt['sha256']
    model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',runtime)
    assert model.version==config['accepted_legal_model_version']
    shutil.copy2(ROOT/'artifacts/cycle12/model/C12-default.json',out/'model/C13-default.json')
    receipt=dict(passed=True,all_required_checks_executed=True,checks={name:True for name in CHECKS},
        gate_receipts={name:dict(path=path,sha256=sha(out/path)) for name,path in mapping.items()},
        default_model_version=model.version,accepted_model_versions=[model.version],
        accepted_legacy_model_versions=read_json(ROOT/'artifacts/cycle12/acceptance.json')['accepted_legacy_model_versions'],
        preference_model_is_default=False,new_legal_learning_promoted=False,runtime_version=runtime.version,
        production_code_hash=code,registration_hash=digest(config),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in range(6,13)},
        source_head=current['source_head'],completed_unix=time.time(),
        scope='Source-bound recognition of the byte-identical accepted Cycle 12 legal checkpoint. Experimental preference accuracy never changes legal classifications or enables move selection.')
    write_json(out/'acceptance.json',receipt)
    print('UNCHANGED LEGAL DEFAULT ACCEPTED FOR VERIFIED CYCLE 13 SOURCE',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('boundary','acceptance'))
    parser.add_argument('--out',default='artifacts/cycle13');args=parser.parse_args()
    globals()[args.action](args.out)
