"""Evidence dependence and temporal experiments; no production policy change."""
import argparse
import copy
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options
from pln_chess.cycle6.history import inspect
from pln_chess.domain import Position
from pln_chess.api import find_move
from evaluation.cycle7_io import pack


from pln_chess.cycle9.temporal import temporal_categories


def temporal(model,rt,out):
    cases=[]
    sources=[('king','6k1/8/8/8/8/8/8/4K2R w K - 0 1',['e1f1']),
             ('rook','6k1/8/8/8/8/8/8/4K2R w K - 0 1',['h1h2']),
             ('pawn-double','7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1',['b7b5']),
             ('promotion','7k/3P4/8/8/8/8/1K6/8 w - - 0 1',['d7d8n'])]
    for family,fen,moves in sources:
        p=Position.from_fen(fen)
        for m in moves:p=p.successor(find_move(p,m))
        history=dict(initial_fen=fen,moves=moves,source='c9-observation/'+family,confidence=.8,castling_history_attested=False)
        for label,mode,evidence in [('unknown','fen-only',None),('metadata','trusted-metadata',dict(source='c9-FEN-claim',confidence=.8)),
                ('events','event-backed',history),('missing','event-backed',{**history,'initial_fen':p.fen(),'moves':[]}),
                ('conflict','event-backed',{**history,'moves':moves+moves})]:
            receipt=inspect(p,mode,evidence);categories=temporal_categories(receipt)
            assert categories['source_receipt_id']==receipt['id']
            if label=='missing':assert not categories['directly_observed_events']
            if label=='conflict':assert categories['status']=='conflicting'
            cases.append(dict(family=family,condition=label,fen=p.fen(),receipt=receipt,categories=categories))
    pack(out/'temporal/categories.json.xz',cases)
    write_json(out/'temporal/summary.json',dict(cases=len(cases),schema='temporal-epistemics-v9',
        explicit_categories=True,native_history_theorem=False,policy_changed=False))


def dependence(rt,out):
    from training.cycle8 import train
    from pln_chess.cycle8.ontology import observe,key
    from pln_chess.evidence import Ledger
    from pln_chess.cycle4.model import observe_example
    full=read_json(ROOT/'artifacts/cycle8/datasets/dataset.json')
    first=next(r for r in full['examples'] if r['movement_label'] and r['move'].endswith('n'))
    identifier=key(observe(Position.from_fen(first['fen']),find_move(Position.from_fen(first['fen']),first['move']))['descriptor'])
    selected=[];seen=set()
    for r in full['examples']:
        p=Position.from_fen(r['fen']);m=find_move(p,r['move'])
        if r['dependence_group'] in seen or key(observe(p,m)['descriptor'])!=identifier:continue
        selected.append(r);seen.add(r['dependence_group'])
        if len(selected)==4:break
    assert len(selected)>=2
    source=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt).source_model()
    def trained(name,rows,variant='C8-promotion-relative',retract=()):
        data=dict(examples=rows,hash=digest(rows));path=out/f'dependence/{name}'
        model=train(data,source,rt,variant,out=path,retract_groups=retract)
        return model
    base=trained('base',selected);replay=trained('replay',selected)
    duplicate=trained('duplicate',selected+selected)
    transformed=copy.deepcopy(selected[0]);transformed['dependence_group']='transformed-file';transformed['transformation_lineage']=[selected[0]['dependence_group']]
    correlated=trained('correlated',selected+[transformed])
    independent=copy.deepcopy(selected[0]);independent['dependence_group']='independent-counterexample';independent['movement_label']=False
    conflict=trained('independent-conflict',selected+[independent])
    same_group=copy.deepcopy(independent);same_group['dependence_group']=selected[0]['dependence_group']
    ambiguous=trained('same-group-conflict',selected+[same_group])
    unsafe=trained('no-dependence',selected+selected,'no-dependence')
    removed=trained('removed',selected,retract=[r['dependence_group'] for r in selected])
    assert base.version==replay.version
    def values(m):return {k:(v['positive'],v['negative']) for k,v in m.hypotheses.items()}
    assert values(base)==values(duplicate)==values(correlated)
    assert not removed.hypotheses and values(base)!=values(unsafe)
    checkpoint=out/'dependence/base/model/C8-promotion-relative.json'
    assert PromotionModel.load(checkpoint,rt).version==base.version
    payload=observe_example(first['fen'],first['move'],first['label'],'c9-ledger-test','c9-ledger-test',None,rt,_payload_only=True)
    ledger_path=out/'dependence/idempotent-ledger.jsonl';ledger=Ledger(ledger_path)
    a=ledger.append(payload);b=ledger.append(payload);assert b['status']=='duplicate' and len(ledger.records())==1
    result=dict(replay_version=base.version,deterministic_replay=True,checkpoint_roundtrip=True,
        ingestion=dict(first=a,second=b,records=len(ledger.records())),duplicate_native_values_identical=True,
        correlated_ancestor_native_values_identical=True,removed_hypotheses=len(removed.hypotheses),
        values={name:values(m) for name,m in [('base',base),('duplicate',duplicate),('correlated',correlated),('independent-conflict',conflict),('same-group-conflict',ambiguous),('no-dependence',unsafe)]},
        reports={name:m.training_report for name,m in [('base',base),('duplicate',duplicate),('correlated',correlated),('independent-conflict',conflict),('same-group-conflict',ambiguous),('no-dependence',unsafe)]},
        caveats=['Duplicate raw training rows change audit ledger digests and model identity, while group-aware native beliefs remain identical.',
                 'A shared group with conflicting labels is excluded entirely; conservative information loss is explicit.',
                 'An unannotated correlated source can still be double counted. Provenance honesty is an external assumption.'],
        production_policy_changed=False)
    write_json(out/'dependence/summary.json',result)


def run(out):
    from scripts.cycle8_controls import negatives,temporal as historical_temporal,transformations
    out=Path(out);rt=Runtime(timeout=300);model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    print('negatives',negatives(model,rt,out),flush=True)
    print('historical temporal',historical_temporal(model,rt,out),flush=True)
    print('transformations',transformations(model,rt,out),flush=True)
    temporal(model,rt,out);dependence(rt,out)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
