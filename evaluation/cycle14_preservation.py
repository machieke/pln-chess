"""Current-source historical concept parity, separately from new research."""
import argparse
from collections import Counter
from pathlib import Path
from pln_chess.common import ROOT,digest,read_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle13.concepts import ForkModel,ForkSession,infer_concepts
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out);runtime=Runtime(timeout=900);options=FieldOptions(timeout_seconds=900)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    concept=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime)
    fork=ForkModel.load(ROOT/'artifacts/cycle13/model/C13-fork-role.json',runtime);session=ForkSession(runtime)
    prior={r['id']:r for name in ('historical','external') for r in read_gzip(ROOT/f'artifacts/cycle13/concepts/{name}.json.xz')}
    cases=[dict(id=r['id'],input={**r['input'],'id':r['id']},split=r['split'],reference=r['reference'])
        for r in read_json(ROOT/'artifacts/cycle12/datasets/concepts.json')['records'] if r['split']!='train']
    cases.extend(dict(r,split='historical-external') for r in read_json(ROOT/'artifacts/cycle13/datasets/external-concepts.json')['records'])
    rows=[]
    for case in cases:
        result=infer_concepts([case['input']],concept,field,fork_model=fork,runtime=runtime,options=options,session=session)
        assert not result['execution']['truncated'];answer=result['concepts'][0];old=prior[case['id']]['result']
        assert digest(answer)==digest(old),(case['id'],'historical native result changed')
        rows.append(dict(id=case['id'],split=case['split'],reference=case['reference'],result=answer,exact_native_proof_parity=True))
    pack(out/'preservation/concepts.json.xz',rows)
    test=[r for r in rows if r['split']=='test'];external=[r for r in rows if r['split']=='historical-external']
    correct=lambda row:row['result']['classification']==('supported' if row['reference']['label'] else 'contradicted')
    assert len(test)==306 and all(correct(r) for r in test)
    assert len(external)==96 and sum(correct(r) for r in external)==28 and sum(r['result']['classification']=='unknown' for r in external)==68
    atomic_json(out/'preservation/concepts.json',dict(passed=True,production_code_hash=production_code_hash(),
        native_proof_rows=len(rows),historical_test_N=306,historical_test_correct=306,
        historical_external_N=96,historical_external_correct=28,historical_external_unknown=68,historical_external_wrong=0,
        all_previous_correct_preserved=True,exact_native_proof_parity=True,artifact_sha256=sha(out/'preservation/concepts.json.xz'),
        scope='Fresh inference under current source; previously exposed historical panels are regression evidence, not new transfer samples.'))
    print('C14 HISTORICAL CONCEPT PARITY',len(rows),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');run(parser.parse_args().out)
