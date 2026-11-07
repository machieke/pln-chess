"""Causal negative regressions and explicit temporal trust controls."""
from pathlib import Path
from dataclasses import replace
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import Cycle7Options, infer_moves, Session
from pln_chess.cycle6.history import inspect
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack

def regressions(model,rt,out):
    out=Path(out);rows=[];sessions={}
    for filename in ('original-49','new-238'):
        old=read_gzip(ROOT/f'artifacts/cycle6/proofs/{filename}.json.xz')
        for r in old:
            p=Position.from_fen(r['fen']);m=find_move(p,r['move']);pair={}
            for condition,suppress in [('intact',()),('removed',tuple(r['removed_families']))]:
                o=Cycle7Options(mode='operational',suppress_families=suppress)
                session=sessions.setdefault(suppress,Session(rt))
                c=infer_moves(p,model,o,rt,[m],session)['candidates'][0];pair[condition]=c
            rows.append({'suite':filename,'fen':r['fen'],'move':r['move'],'removed_families':r['removed_families'],**pair,
                'intact_negative':pair['intact']['classification']=='supported-illegal',
                'removed_unknown':pair['removed']['classification']=='unknown',
                'C6_native_proof_parity':pair['intact']['proof_trace']==r['C6']['proof_trace']})
    pack(out/f'proofs/{model.variant}-negative-controls.json.xz',rows)
    summary={'model_version':model.version,'cases':len(rows),'intact_negative':sum(r['intact_negative'] for r in rows),
        'removed_unknown':sum(r['removed_unknown'] for r in rows),'exact_native_proof_parity':sum(r['C6_native_proof_parity'] for r in rows),
        'regressions':[{'fen':r['fen'],'move':r['move'],'intact':r['intact']['classification'],'removed':r['removed']['classification']} for r in rows if not r['intact_negative'] or not r['removed_unknown']]}
    write_json(out/f'{model.variant}-negative-regressions.json',summary)
    return summary

def temporal(model,rt,out):
    cases=[];validation=[]
    for name,start,event,move in [('castle','6k1/8/8/8/8/8/8/4K2R b K - 0 1','g8h8','e1g1'),
                                  ('en-passant','7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1','b7b5','c5b6')]:
        p=Position.from_fen(start);q=p.successor(find_move(p,event));history={'initial_fen':start,'moves':[event],
            'source':'C7-supplied-event-'+name,'confidence':.99,'castling_history_attested':True}
        conditions=[('FEN-only','fen-only',None),('trusted-metadata','trusted-metadata',{'source':'C7-metadata-claim','confidence':.8}),
            ('validated-history','event-backed',history),('unknown-history','event-backed',{'source':'C7-unknown-events','confidence':0.0,'initial_fen':q.fen(),'moves':[]}),
            ('inconsistent-history','event-backed',{**history,'moves':[event,event]}),
            ('truncated-history','event-backed',{**history,'initial_fen':q.fen(),'moves':[],'castling_history_attested':False})]
        for trust in ('trusted-metadata','event-backed'):
            try:inspect(q,trust,None)
            except ValueError as error:validation.append({'name':name,'mode':trust,'input':None,'rejected':True,'error':str(error)})
            else:raise AssertionError('Missing source was accepted as trusted history')
        for condition,trust,evidence in conditions:
            receipt=inspect(q,trust,evidence)
            for mode in ('operational','strict','experimental'):
                c=infer_moves(q,model,Cycle7Options(mode=mode,temporal_mode=trust,temporal_evidence=evidence),rt,[find_move(q,move)])['candidates'][0]
                cases.append({'name':name,'condition':condition,'mode':mode,'fen':q.fen(),'move':move,'receipt':receipt,'candidate':c,
                    'observed':'FEN board and supplied event strings','assumed':'Source confidence and initial rights metadata',
                    'inferred':'Structural consistency of replay; historical legality remains unverified.'})
    pack(Path(out)/'temporal.json.xz',cases)
    write_json(Path(out)/'temporal-validation.json',validation)
    assert all(not r['candidate']['positive_proof_complete'] for r in cases)
    assert all(r['candidate']['classification']=='unknown' for r in cases if r['condition']=='inconsistent-history')
    return {'cases':len(cases),'native_positive_history_theorem':False}

if __name__=='__main__':
    import sys
    out=Path(sys.argv[1]);rt=Runtime(timeout=180)
    for variant in ('C7-frozen','C7-learned-8'):
        model=BackoffModel.load(out/f'model/{variant}.json',rt)
        print(variant,regressions(model,rt,out),flush=True)
    print(temporal(BackoffModel.load(out/'model/C7-frozen.json',rt),rt,out),flush=True)
