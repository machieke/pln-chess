"""Score-blind bounded response panel; oracle enumeration remains offline."""
import argparse
from pathlib import Path
import chess
from pln_chess.common import digest,read_json
from training.cycle14_labels import atomic_json
from training.cycle14_reference import board_from_history


def register(out):
    out=Path(out);population=read_json(out/'datasets/temporal-registration.json')
    rows=sorted((r for r in population['records'] if r['split']=='test'),key=lambda r:digest(['c14-response-panel',r['id']]))[:10]
    assert len(rows)==10
    payload=dict(schema='c14-response-registration-v1',temporal_registration_hash=population['hash'],records=rows,
        maximum_responses_per_candidate=3,
        policy='Retain the registered teacher PV; add up to two hash-sampled legal responses and hash-sampled actor continuations without consulting scores or PLN outputs.',
        horizons=[2,3],new_independent_groups=10,already_counted_in_primary_test=True,
        diagnostic_cases=[dict(id='controlled-king-exposure',fen='4r1k1/8/8/8/8/8/4R3/4K3 w - - 0 1',
            branches={'A':[['e2f2','g8g7']],'B':[['e2e3','g8g7']]},
            expected='Candidate A exposes its king; retain only as an explicitly illegal diagnostic branch'),
            dict(id='controlled-missing-context',fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
                branches={'A':[['a1a2']],'B':[['a1b1']]},expected='Missing second/third endpoints remain incomplete')],
        prediction_or_label_filtering=False)
    payload['hash']=digest(payload);atomic_json(out/'datasets/response-panel-registration.json',payload);return payload


def bind(out):
    out=Path(out);registration=register(out);plans={r['id']:r for r in read_json(out/'datasets/temporal-plans.json')['records']}
    records=[];comparisons=[]
    for selected in registration['records']:
        plan=plans[selected['id']];branches={};coverage={}
        for side,move in zip(('A','B'),plan['moves']):
            board=board_from_history(plan['history'],plan['fen']);board.push_uci(move)
            legal=sorted(m.uci() for m in board.legal_moves);primary=plan['branches'][side] or [move]
            alternatives=[primary];used={primary[1]} if len(primary)>1 else set()
            sampled=sorted((reply for reply in legal if reply not in used),key=lambda reply:digest(['c14-sampled-response',plan['id'],side,reply]))[:2]
            for reply in sampled:
                endpoint=board.copy();endpoint.push_uci(reply);line=[move,reply]
                next_moves=sorted((m.uci() for m in endpoint.legal_moves),key=lambda m:digest(['c14-sampled-continuation',plan['id'],side,reply,m]))
                if next_moves:line.append(next_moves[0])
                alternatives.append(line)
            branches[side]=alternatives
            coverage[side]=dict(known_legal_reply_count=len(legal),examined_distinct_replies=len({line[1] for line in alternatives if len(line)>1}),
                unexamined_legal_replies=len(set(legal)-{line[1] for line in alternatives if len(line)>1}),
                reply_count_source='Offline python-chess legal enumeration; not a production belief or feature')
        records.append({**plan,'branches':branches,'coverage':coverage,'response_selection':registration['policy']})
        for a,line_a in enumerate(branches['A']):
            for b,line_b in enumerate(branches['B']):
                for horizon in (2,3):
                    comparisons.append({**plan,'id':plan['id']+f'-response-A{a}-B{b}-ply{horizon}',
                        'branches':{'A':line_a,'B':line_b},'branch_indices':{'A':a,'B':b},'horizon':horizon,
                        'primary_label_reuse':plan['id']+f'-ply{horizon}' if a==b==0 else None})
    payload=dict(schema='c14-bounded-response-plans-v1',registration_hash=registration['hash'],records=records,
        comparisons=comparisons,independent_groups=len(records),global_robust_preference_claim=False)
    payload['hash']=digest(payload);atomic_json(out/'datasets/response-plans.json',payload);return payload


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('register','bind'));parser.add_argument('--out',default='artifacts/cycle14')
    args=parser.parse_args();result=(register if args.stage=='register' else bind)(args.out);print(result['hash'])
