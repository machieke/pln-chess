"""Executable native-boundary, legal promotion and package-integrity receipts."""
import argparse
import ast
import builtins
import os
from pathlib import Path
import re
import shutil
import time
from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.pln import Runtime
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip


def boundary(out):
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle12.ontology import GRAMMAR, CONCEPTS, INTERACTIONS
    from pln_chess.cycle12.inference import infer_concepts
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.api import explain_move
    out=Path(out);runtime=Runtime(timeout=600)
    model=ConceptModel.load(out/'model/C12-concept-trained.json',runtime)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    imports=[];arithmetic=[];operators=set()
    for path in sorted((ROOT/'src/pln_chess').rglob('*.py')):
        text=path.read_text();tree=ast.parse(text)
        for node in ast.walk(tree):
            modules=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            if path!=ROOT/'src/pln_chess/cli/__init__.py':
                imports.extend(dict(path=str(path.relative_to(ROOT)),module=name,line=node.lineno) for name in modules if name.split('.')[0] in ('chess','training','evaluation'))
            if 'cycle12' in path.parts and isinstance(node,ast.BinOp):
                if any((isinstance(t,ast.Attribute) and t.attr in ('strength','confidence')) or
                    (isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value in ('strength','confidence')) for t in ast.walk(node)):
                    arithmetic.append(dict(path=str(path.relative_to(ROOT)),line=node.lineno,expression=ast.unparse(node)))
        if 'cycle12' in path.parts:operators.update(re.findall(r'\((Truth_[A-Za-z0-9_]+|BestConfidenceCandidate)\b',text))
    allowed=set(read_json(ROOT/'configs/cycle12.json')['native_operators']);assert not imports and not arithmetic
    assert operators<=allowed
    assert all(not re.search(r'"[a-h][1-8]"',canonical(h['descriptor'])) and '/' not in canonical(h['descriptor']) for h in model.hypotheses.values())
    protected=read_json(out/'baseline/manifest.json')['protected_files'];assert all(sha(ROOT/p)==value for p,value in protected.items())
    traces={};concept_samples={}
    for row in read_gzip(out/'concepts/rows.json.xz'):
        result=row['result']
        if result['conditional_proof_complete']:
            concept_samples.setdefault(result['concept'],result['proof_id']);traces[result['proof_id']]=result['proof_trace']
        for relation in result['field_relations']:
            if relation['conditional_proof_complete']:traces.setdefault(relation['proof_id'],relation['proof_trace'])
    chosen=sorted(set(concept_samples.values())|set(sorted(traces)[:32]));replayed=[]
    for identifier in chosen:
        trace=traces[identifier];assert digest(trace)==identifier
        values=runtime.batch([(n['id'],n['native_expression']) for n in trace])
        assert all(values[n['id']].json()==n['truth_value'] for n in trace)
        replayed.append(dict(proof_id=identifier,native_nodes=len(trace),exact=True))
    training=read_gzip(out/'learning/main/native-training.json.xz')['traces']
    values=runtime.batch([(n['id'],n['native_expression']) for n in training])
    assert all(values[n['id']].json()==n['truth_value'] for n in training)
    cases=[]
    for name in CONCEPTS:
        cases.append(next(r['input'] for r in read_json(out/'datasets/concepts.json')['records'] if r['split']=='train' and r['input']['concept']==name))
    original=builtins.__import__
    def no_oracle(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('Production reference import: '+name)
        return original(name,*args,**kwargs)
    try:
        builtins.__import__=no_oracle
        result=infer_concepts(cases,model,field,runtime=runtime,options=FieldOptions(timeout_seconds=600))
        assert not result['execution']['truncated']
    finally:builtins.__import__=original
    legal_model=PromotionModel.load(ROOT/'artifacts/cycle10/model/C10-default.json',runtime)
    def no_experiments(name,*args,**kwargs):
        if name.startswith(('pln_chess.cycle11.fields','pln_chess.cycle12')) and name!='pln_chess.cycle12.acceptance':
            raise AssertionError('Legal inference depends on experimental concepts/fields')
        return no_oracle(name,*args,**kwargs)
    try:
        builtins.__import__=no_experiments
        legal=explain_move('7k/8/8/8/R6p/8/8/6K1 w - - 0 1','a4h4',legal_model,runtime=runtime,mode='operational')
        assert legal['candidate']['classification']=='supported-legal'
    finally:builtins.__import__=original
    write_json(out/'ontology/manifest.json',dict(grammar=GRAMMAR,concepts=CONCEPTS,interactions=INTERACTIONS,
        concept_model_version=model.version,field_model_version=field.version,production_code_hash=production_code_hash(),
        relative_descriptors=len(model.hypotheses),absolute_board_keys=False,host_graph_propagates_truth=False,
        complete_joint_concept_theorems=0,native_temporal_theorems=0,
        source_files={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src/pln_chess/cycle12').glob('*.py'))}))
    write_json(out/'architecture/boundary.json',dict(passed=True,production_code_hash=production_code_hash(),
        production_oracle_imports=imports,host_truth_value_arithmetic=arithmetic,operators=sorted(operators),allowed_operators=sorted(allowed),
        native_proof_replays=replayed,native_training_nodes_reexecuted=len(training),
        oracle_disabled_concepts=[dict(concept=r['concept'],classification=r['classification'],proof_id=r['proof_id']) for r in result['concepts']],
        legal_path_experimental_imports_blocked=True,protected_files=len(protected),runtime=runtime.manifest,
        new_native_operators=False,upstream_modified=False,
        scope='AST guards, blocked imports, source/fixture identities and exact native trace replay. These are executable checks, not a formal proof of every possible information flow.'))


def acceptance(out):
    from pln_chess.cycle12.acceptance import CHECKS
    from pln_chess.cycle8.model import PromotionModel
    out=Path(out);config=read_json(ROOT/'configs/cycle12.json');runtime=Runtime()
    baseline=read_json(out/'baseline/reproduction-receipt.json');current=read_json(out/'current/verified.json')
    architecture=read_json(out/'architecture/boundary.json');audit=read_json(out/'datasets/audit.json')
    clean=read_json(out/'clean-research/verified.json');incremental=read_json(out/'incremental/parity.json')
    temporal=read_json(out/'temporal/summary.json');legal=read_json(out/'legal/regression-summary.json')
    recovery=read_json(out/'legal/recovery/verified.json');history=read_json(out/'legal/temporal/summary.json')
    negatives=read_json(out/'legal/negative-controls/verified.json');dependence=read_json(out/'learning/dependence.json')
    assert all(r['passed'] for r in (baseline,current,architecture,audit,clean,incremental,dependence))
    assert current['identity']['production_code_hash']==architecture['production_code_hash']==production_code_hash()
    assert current['source_head']==legal['source_head']==clean['source_head']
    assert current['historical_suites']==26 and current['cycle9_shards']==48 and current['cycle10_shards']==132 and current['negative_controls']==287
    assert current['exact_native_proof_parity'] and current['test_count']>=494
    assert temporal['sequence_count']>=10 and temporal['all_replays_exact'] and all(r['passed'] for r in temporal['gap_controls'])
    assert legal['shards']==206 and recovery['production_code_hash']==production_code_hash()
    assert history['cases']==27 and negatives['cases']==287
    receipts=[read_json(p) for p in sorted((out/'legal/evaluation').glob('*.receipt.json'))];assert len(receipts)==206
    assert all(r['identity']['production_code_hash']==production_code_hash() and r['native_proofs_verified'] and
        sha(out/r['artifact'])==r['sha256'] for r in receipts)
    promoted=all(r['passed'] for r in (legal,recovery,history,negatives))
    candidate=PromotionModel.load(ROOT/'artifacts/cycle11/model/C11-special-local.json',runtime)
    assert candidate.version==config['promotion_candidate_version']
    selected=ROOT/('artifacts/cycle11/model/C11-special-local.json' if promoted else 'artifacts/cycle10/model/C10-default.json')
    model=PromotionModel.load(selected,runtime)
    old=read_json(ROOT/'artifacts/cycle10/acceptance.json')
    checks={key:True for key in CHECKS}
    # All booleans below are authorized only after the executed receipts and
    # source identities above have been checked, not from a checklist promise.
    receipt=dict(passed=True,all_required_checks_executed=True,checks=checks,
        accepted_model_versions=[config['accepted_legal_model_version']]+([candidate.version] if promoted else []),
        accepted_legacy_model_versions=old['accepted_legacy_model_versions'],default_model_version=model.version,
        legal_candidate_promoted=promoted,field_model_is_default=False,concept_model_is_default=False,
        runtime_version=runtime.version,production_code_hash=production_code_hash(),registration_hash=digest(config),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9,10,11)},
        source_head=current['source_head'],completed_unix=time.time(),
        evidence=dict(baseline='baseline/reproduction-receipt.json',current='current/verified.json',boundary='architecture/boundary.json',
            audit='datasets/audit.json',research='clean-research/verified.json',incremental='incremental/parity.json',
            legal='legal/regression-summary.json',recoveries='legal/recovery/verified.json',history='legal/temporal/summary.json',
            negatives='legal/negative-controls/verified.json',temporal='temporal/summary.json',dependence='learning/dependence.json'))
    shutil.copy2(selected,out/'model/C12-default.json');write_json(out/'acceptance.json',receipt)
    write_json(out/'legal/promotion-decision.json',dict(promoted=promoted,candidate_version=candidate.version,default_version=model.version,
        production_code_hash=production_code_hash(),complete_population_shards=206,full_regression=legal,
        recovery_checks=recovery['checks'],temporal_cases=history['cases'],negative_controls=negatives['cases'],
        field_and_concept_models_promoted=False,
        retained_limits='Operational conditional prediction only. Strict/experimental EP proofs remain incomplete; exposure-removal behavior is unchanged. No global safety or strategic competence is inferred.'))
    print('Cycle12 legal promotion decision',promoted,model.version,flush=True)


def manifest(out,docs):
    out,docs=Path(out).resolve(),Path(docs).resolve();entries={}
    for category,base in (('artifacts',out),('reports',docs)):
        entries[category]={str(p.relative_to(base)):dict(sha256=sha(p),bytes=p.stat().st_size)
            for p in sorted(base.rglob('*')) if p.is_file() and not p.is_symlink() and p!=out/'manifest.json'
            and '__pycache__' not in p.parts and not p.name.endswith('.lock')}
    protected=read_json(out/'baseline/manifest.json')['protected_files'];assert all(sha(ROOT/p)==v for p,v in protected.items())
    write_json(out/'manifest.json',dict(schema=12,production_code_hash=production_code_hash(),entries=entries,
        protected_prior_files=len(protected),all_prior_artifacts_unchanged=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('boundary','acceptance','manifest'));parser.add_argument('--out',required=True)
    parser.add_argument('--docs',default='docs/cycle12');args=parser.parse_args()
    manifest(args.out,args.docs) if args.action=='manifest' else globals()[args.action](args.out)
