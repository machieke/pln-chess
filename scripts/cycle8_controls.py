"""Causal evidence controls and complete-payload transfer demonstrations."""
from pathlib import Path
from dataclasses import replace
import argparse
import copy
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options,Session
from pln_chess.cycle8.ontology import observe
from pln_chess.cycle4.ontology import descriptors
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from pln_chess.cycle6.history import inspect


def negatives(model,rt,out):
    rows=[];sessions={}
    for filename in ('original-49','new-238'):
        for old in read_gzip(ROOT/f'artifacts/cycle6/proofs/{filename}.json.xz'):
            pos=Position.from_fen(old['fen']);move=find_move(pos,old['move']);pair={}
            for label,suppressed in [('intact',()),('removed',tuple(old['removed_families']))]:
                options=Cycle8Options(mode='operational',suppress_families=suppressed,timeout_seconds=180)
                session=sessions.setdefault(suppressed,Session(rt))
                pair[label]=infer_moves(pos,model,options,rt,[move],session)['candidates'][0]
            rows.append({'suite':filename,'fen':old['fen'],'move':old['move'],'removed_families':old['removed_families'],**pair,
                'intact_negative':pair['intact']['classification']=='supported-illegal',
                'removed_unknown':pair['removed']['classification']=='unknown',
                'historical_native_proof_parity':pair['intact']['proof_trace']==old['C6']['proof_trace']})
    pack(out/f'proofs/{model.variant}-negative-controls.json.xz',rows)
    summary={'model_version':model.version,'cases':len(rows),'intact_negative':sum(r['intact_negative'] for r in rows),
        'removed_unknown':sum(r['removed_unknown'] for r in rows),
        'exact_native_proof_parity':sum(r['historical_native_proof_parity'] for r in rows),
        'failures':[{'fen':r['fen'],'move':r['move'],'intact':r['intact']['classification'],'removed':r['removed']['classification']} for r in rows if not r['intact_negative'] or not r['removed_unknown']]}
    write_json(out/f'{model.variant}-negative-regressions.json',summary);return summary


def transfers(model,rt,out):
    data=read_json(out/'datasets/dataset.json')
    ledger=read_gzip(out/f'training/{model.variant}-ledger.json.xz')
    evidence={r['evidence_id']:r['payload'] for r in ledger['records']}
    attempts=[];successful=[];seen=set();options=Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180)
    # Registration chooses all focus moves in held-out structural/validation families; success is not presumed.
    for fixture in data['positions']:
        if fixture['split'] not in ('validation','combination-holdout','adversarial') or not fixture.get('focus_move') or fixture.get('unknown_squares'):continue
        p=Position.from_fen(fixture['fen'])
        notation=fixture['focus_move'][:-1]+('q','r','b','n')[len(attempts)%4]
        move=find_move(p,notation)
        full=infer_moves(p,model,options,rt,[move]);item=full['candidates'][0]
        expected=chess.Move.from_uci(notation) in chess.Board(fixture['fen']).legal_moves
        correct=item['classification']==('supported-legal' if expected else 'supported-illegal')
        selection=item.get('promotion_selection');record={'fixture':fixture,'candidate':item,'budget':full['budget'],
            'expected_legal':expected,'correct_supported_decision':correct}
        if not selection or item['classification'] not in ('supported-legal','supported-illegal'):
            record['outcome']='no-new-supported-transition';attempts.append(record);continue
        if not correct:
            record['outcome']='incorrect-supported-transition';attempts.append(record);continue
        hypothesis=model.hypotheses[selection['rule_id']]
        before=observe(p,move)['descriptor'];source_records=[evidence[e] for e in hypothesis['evidence_ids']]
        # Complete-context mismatch is explicit: new board, game/family, and transformation lineage.
        assert all(e['input']['fen']!=p.fen() for e in source_records)
        assert all(e['structural_family']!=fixture['structural_family'] for e in source_records)
        context_hash=digest(descriptors(p,move)['context'])
        source_context_hashes=[]
        for evidence_record in source_records:
            training_position=Position.from_fen(evidence_record['input']['fen'])
            training_move=find_move(training_position,evidence_record['input']['move'])
            source_context_hashes.append(digest(descriptors(training_position,training_move)['context']))
        if context_hash in source_context_hashes:
            record['outcome']='exact-context-control-excluded-from-transfer-count';attempts.append(record);continue
        stripped=copy.deepcopy(model);stripped.hypotheses.pop(selection['rule_id'])
        removed=infer_moves(p,stripped,options,rt,[move])['candidates'][0]
        essential=set(hypothesis['evidence_ids'])
        changed=removed['classification']!=item['classification'] or removed['raw_stv']!=item['raw_stv']
        assert not essential&set(removed['evidence_ids'])
        # This removes the complete learned evidence family; replay-specific group retraction is also unit-tested.
        record.update(outcome='supported-transfer-with-removal' if changed else 'nonessential-new-evidence',
            training_evidence=source_records,relative_descriptor=before,rule_id=selection['rule_id'],
            native_expressions=[n['native_expression'] for n in item['proof_trace']],raw_truth_value=item['raw_stv'],
            removed_hypothesis_evidence_ids=sorted(essential),removed=removed,
            control='Remove the entire selected learned hypothesis and replay unchanged inference.',
            complete_context_match=False,local_category_match=True,
            heldout_context_hash=context_hash,training_context_hashes=source_context_hashes,
            transfer_scope='Shared relative local transition, not an absolute position or complete-context match; no unseen-type extrapolation claim.')
        attempts.append(record)
        signature=(fixture['structural_family'],p.turn,item['classification'],move.promotion)
        if changed and signature not in seen:
            seen.add(signature);successful.append(record)
    pack(out/'proofs/transfer-attempts.json.xz',attempts)
    # Prefer strict combination/adversarial holdouts, with one representative per source group.
    representatives=[];representative_groups=set()
    for record in sorted(successful,key=lambda r:({'combination-holdout':0,'adversarial':1,'validation':2}[r['fixture']['split']],r['fixture']['id'])):
        group=record['fixture']['dependence_group']
        if group not in representative_groups and len(representatives)<10:
            representatives.append(record);representative_groups.add(group)
    pack(out/'proofs/representative-transfers.json.xz',representatives)
    summary={'attempts':len(attempts),'successful_distinct_demonstrations':len(successful),
        'successful_source_groups':len({r['fixture']['dependence_group'] for r in successful}),
        'strict_holdout_source_groups':len({r['fixture']['dependence_group'] for r in successful if r['fixture']['split']!='validation'}),
        'at_least_five':len(representatives)>=5,'representatives':[{k:r[k] for k in ('fixture','relative_descriptor','rule_id','raw_truth_value','control')} for r in representatives],
        'scope':'Constructed disjoint structural families. Local categories intentionally overlap. Color mirrors within a group are not counted as independent acquisition.'}
    write_json(out/'transfers.json',summary);return summary


def original_errors(model,rt,out):
    inventory=read_json(out/'promotion-errors.json');rows=[]
    for old in inventory['cases']:
        p=Position.from_fen(old['fen']);m=find_move(p,old['move'])
        c=infer_moves(p,model,Cycle8Options(mode='operational',timeout_seconds=180),rt,[m])['candidates'][0]
        wrong=(c['classification']=='supported-legal' and not old['expected_legal']) or (c['classification']=='supported-illegal' and old['expected_legal'])
        rows.append({'case_id':old['id'],'fen':old['fen'],'move':old['move'],'expected_legal':old['expected_legal'],
            'old_classification':old['actual_classification'],'candidate':c,'error_remaining':wrong,
            'correct_supported_decision':c['classification']==('supported-legal' if old['expected_legal'] else 'supported-illegal')})
    pack(out/f'proofs/{model.variant}-original-errors.json.xz',rows)
    summary={'cases':len(rows),'errors_remaining':sum(r['error_remaining'] for r in rows),
        'correct_supported_decisions':sum(r['correct_supported_decision'] for r in rows),
        'abstentions':sum(r['candidate']['classification']=='unknown' for r in rows),
        'incomplete':sum(r['candidate']['classification']=='incomplete' for r in rows)}
    write_json(out/f'{model.variant}-original-errors.json',summary);return summary


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
                c=infer_moves(q,model,Cycle8Options(mode=mode,temporal_mode=trust,temporal_evidence=evidence),rt,[find_move(q,move)])['candidates'][0]
                cases.append({'name':name,'condition':condition,'mode':mode,'fen':q.fen(),'move':move,'receipt':receipt,'candidate':c,
                    'observed':'FEN board and supplied event strings','assumed':'Source confidence and initial rights metadata',
                    'inferred':'Structural consistency of replay; historical legality remains unverified.'})
    pack(Path(out)/f'{model.variant}-temporal.json.xz',cases)
    write_json(Path(out)/f'{model.variant}-temporal-validation.json',validation)
    assert all(not r['candidate']['positive_proof_complete'] for r in cases)
    assert all(r['candidate']['classification']=='unknown' for r in cases if r['condition']=='inconsistent-history')
    return {'cases':len(cases),'native_positive_history_theorem':False}


def transformations(model,rt,out):
    from pln_chess.spatial import translate,reflect_files,color_flip
    rows=[]
    for fen,notation in [("5k2/3P4/8/8/8/8/1K6/8 w - - 0 1","d7d8"),("4n3/3P4/6k1/8/8/8/1K6/8 w - - 0 1","d7e8")]:
        p=Position.from_fen(fen)
        for choice in ("q","r","b","n"):
            m=find_move(p,notation+choice);base=observe(p,m)["descriptor"]
            variants=[("original",p,m),("file-translation",translate(p,(1,0)),replace(m,start=(m.start[0]+1,m.start[1]),end=(m.end[0]+1,m.end[1]))),("file-reflection",reflect_files(p),replace(m,start=(7-m.start[0],m.start[1]),end=(7-m.end[0],m.end[1]))),("color-relative",color_flip(p),replace(m,start=(m.start[0],7-m.start[1]),end=(m.end[0],7-m.end[1])))]
            for name,q,n in variants:
                descriptor=observe(q,n)["descriptor"];assert descriptor==base
                c=infer_moves(q,model,Cycle8Options(mode="operational"),rt,[n])["candidates"][0]
                expected=chess.Move.from_uci(n.notation) in chess.Board(q.fen()).legal_moves
                rows.append({"transformation":name,"fen":q.fen(),"move":n.notation,"descriptor":descriptor,"candidate":c,"expected_legal":expected,"correct_supported":c["classification"]==("supported-legal" if expected else "supported-illegal")})
    pack(out/"proofs/transformations.json.xz",rows)
    result={"cases":len(rows),"equal_relative_descriptors":True,"correct_supported":sum(r["correct_supported"] for r in rows),"unknown":sum(r["candidate"]["classification"]=="unknown" for r in rows),"scope":"Metamorphic controls; transformed cases share ancestry and are not independent holdouts."}
    write_json(out/"transformations.json",result);return result

def run(out,variant):
    out=Path(out);rt=Runtime(timeout=180);model=PromotionModel.load(out/f'model/{variant}.json',rt)
    print('negative controls',negatives(model,rt,out),flush=True)
    print('original errors',original_errors(model,rt,out),flush=True)
    print('temporal',temporal(model,rt,out),flush=True)
    if variant=='C8-promotion-relative':
        print('transfers',transfers(model,rt,out),flush=True)
        print('transformations',transformations(model,rt,out),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--variant',required=True)
    args=parser.parse_args();run(args.out,args.variant)
