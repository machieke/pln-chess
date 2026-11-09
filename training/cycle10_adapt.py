"""Registered nested external adaptation and dependence ablations, offline only."""
import argparse
from collections import defaultdict
import copy
from dataclasses import asdict
from pathlib import Path
import time

import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime,TV
from pln_chess.learning import PRIOR
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle7.model import key as local_key
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.ontology import observe as promotion_observe,key as promotion_key
from training.cycle4 import enrich4
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


def select(data,model):
    """No final-test records or model errors are consulted by the selector."""
    source=model.source_model();base=source.source['source']['base']['hypotheses'];bygame=defaultdict(list);audit=[]
    fixtures={f['id']:f for f in data['positions'] if f['split']=='external-adaptation'}
    for fixture in fixtures.values():
        p=Position.from_fen(fixture['fen'])
        for move in candidates(p):
            if not all(0<=v<8 for v in move.end):continue
            rel=next(r for r in descriptors(p,move)['relations'] if r['target']=='LocalAdmissibility')
            promo=promotion_observe(p,move) if move.promotion else None
            identifier=promotion_key(promo['descriptor']) if promo else local_key(rel['descriptor'],0)
            known=(identifier in model.hypotheses) if promo else (rel['id'] in base or identifier in source.hypotheses)
            bygame[fixture['source_game']].append(dict(fixture=fixture['id'],fen=fixture['fen'],move=move.notation,
                identifier=identifier,descriptor=promo['descriptor'] if promo else rel['descriptor'],channel='promotion' if promo else 'local',
                rank=int(known),source_collection=fixture['source_collection'],opening_family=fixture['opening_family']))
    examples=[]
    for game,pool in sorted(bygame.items()):
        chosen=[];seen=set()
        for row in sorted(pool,key=lambda r:(r['rank'],digest([r['identifier'],r['fixture'],r['move']]))):
            if row['identifier'] in seen:continue
            chosen.append(row);seen.add(row['identifier'])
            if len(chosen)==16:break
        for row in chosen:
            b=chess.Board(row['fen']);move=chess.Move.from_uci(row['move'])
            observation=enrich4(dict(fen=row['fen'],move=row['move'],label=move in b.legal_moves,
                source='external-PGN/'+row['source_collection']+'/'+game,dependence_group=game,
                transformation_lineage=['opening/'+row['opening_family']],confidence=.5,split='train',
                family='opening/'+row['opening_family'],position_fixture=row['fixture']))
            examples.append({**row,**observation, 'source_game':game})
        audit.append(dict(game=game,pool=len(pool),selected=chosen))
    return examples,dict(label_blind_selection=True,examples_per_game=16,ranking='Unseen exact relative conditionals first, then deterministic content hash; labels added after selection.',games=audit)


def revise(frozen,rows,runtime,policy='game-and-opening',name='experimental',out=None):
    """Extend existing learned conditional maps using only Truth_Revision."""
    if policy not in ('game-and-opening','game-only','unsafe-row-independent'):raise ValueError('Unknown dependence policy')
    model=copy.deepcopy(frozen);source=model.source_model();ledger=[];bykey=defaultdict(list)
    for row in rows:
        payload=dict(input=dict(fen=row['fen'],move=row['move']),source=row['source'],source_game=row['source_game'],
            dependence_group=row['dependence_group'],transformation_lineage=row.get('transformation_lineage',[]),
            target='LocalAdmissibility',descriptor=row['descriptor'],channel=row['channel'],
            local_transition_label=row['movement_label'],global_reference_label=row['label'],
            observation_tv=TV(float(row['movement_label']),row['confidence']).json(),runtime_version=runtime.version,
            original_fixture=row['position_fixture'],scope='Externally sourced position, offline pseudo-legality supervision; no global safety claim.')
        evidence=digest(payload);ledger.append(dict(evidence_id=evidence,payload=payload));bykey[row['channel'],row['identifier']].append((evidence,payload))
    jobs=[];states={};excluded=[]
    for (channel,identifier),observations in sorted(bykey.items()):
        store=model.hypotheses if channel=='promotion' else source.hypotheses;existing=store.get(identifier)
        groups=set(existing['dependence_groups']) if existing else set();ids=list(existing['evidence_ids']) if existing else []
        positive=list(existing['supporting_evidence']) if existing else [];negative=list(existing['contradicting_evidence']) if existing else []
        refs=[TV.from_json(existing[k]).metta() if existing else PRIOR.metta() for k in ('positive','negative')]
        grouped=defaultdict(list)
        for i,(e,p) in enumerate(observations):
            group=str(i) if policy=='unsafe-row-independent' else p['dependence_group'];grouped[group].append((e,p))
        changed=False
        for group,records in sorted(grouped.items()):
            if len({p['local_transition_label'] for _,p in records})>1:
                excluded.extend(dict(evidence=e,hypothesis=identifier,reason='contradictory observations in one source game') for e,_ in records);continue
            e,p=records[0];ancestry={p['dependence_group']}
            if policy=='game-and-opening':ancestry.update(p['transformation_lineage'])
            if policy!='unsafe-row-independent' and (ancestry&groups or e in ids):
                excluded.extend(dict(evidence=x,hypothesis=identifier,reason='shared game, opening or transformation ancestry') for x,_ in records);continue
            changed=True;groups.update(ancestry);ids.append(e);(positive if p['local_transition_label'] else negative).append(e)
            excluded.extend(dict(evidence=x,hypothesis=identifier,reason='same game already counted') for x,_ in records[1:])
            for index,label in enumerate((p['local_transition_label'],not p['local_transition_label'])):
                node=f'c10revision{len(jobs)}';jobs.append((node,f'(Truth_Revision {refs[index]} {TV(float(label),p["observation_tv"]["confidence"]).metta()})'));refs[index]=f'({node})'
        if not changed:continue
        states[channel,identifier]=dict(id=identifier,descriptor=observations[0][1]['descriptor'],target='LocalAdmissibility',tier=4,
            evidence_ids=ids,supporting_evidence=positive,contradicting_evidence=negative,dependence_groups=sorted(groups),
            refs=refs,origin='native-revision-of-external-relative-observations',**({} if channel=='promotion' else dict(level=0,new_training=True)))
    values=runtime.batch(jobs) if jobs else {}
    for (channel,identifier),state in states.items():
        refs=state.pop('refs');record={**state,'positive':values[refs[0][1:-1]].json(),'negative':values[refs[1][1:-1]].json()}
        (model.hypotheses if channel=='promotion' else source.hypotheses)[identifier]=record
    source.variant='C10-external-'+name;source.training_report={**source.training_report,'C10_external_revision':True}
    model.source=asdict(source);model.variant='C10-external-'+name
    model.training_report=dict(base_model_version=frozen.version,new_learning_promoted=False,policy=policy,
        records=len(ledger),source_games=len({r['source_game'] for r in rows}),opening_families=len({r['opening_family'] for r in rows}),
        revised_hypotheses=len(states),native_revision_nodes=len(jobs),excluded_records=len(excluded),ledger_digest=digest(ledger),
        frozen_source_preserved=source.source==frozen.source_model().source,
        scope='Experimental exact relative conditionals only; existing native formulas, inference thresholds and C8 default unchanged.')
    if out:
        out=Path(out);model.export(out/f'model/{name}.json')
        pack(out/f'training/{name}.json.xz',dict(records=ledger,excluded=excluded,native_revision_expressions=jobs,
            native_revision_outputs={k:v.json() for k,v in values.items()},training_report=model.training_report))
    return model


def run(out):
    out=Path(out);receipt=read_json(out/'frozen-complete.json');assert receipt['passed']
    assert sha(out/'calibration/frozen-evaluation.json')==receipt['frozen_calibration_sha256']
    assert all(sha(out/p)==h for p,h in receipt['receipts'].items())
    data=read_json(out/'datasets/dataset.json');assert data['hash']==receipt['dataset_hash']
    runtime=Runtime(timeout=600);frozen=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',runtime)
    rows,selection=select(data,frozen);write_json(out/'adaptation/selection.json',selection);pack(out/'adaptation/examples.json.xz',rows)
    games=defaultdict(list)
    for game in data['games']:
        if game['split']=='external-adaptation':games[game['source_collection']].append(game['id'])
    small={game for source,ids in sorted(games.items()) for game in sorted(ids)[:2]};assert len(small)==6
    results={}
    for name,selected in [('small',[r for r in rows if r['source_game'] in small]),('large',rows)]:
        model=revise(frozen,selected,runtime,name=name,out=out/'adaptation')
        assert PromotionModel.load(out/f'adaptation/model/{name}.json',runtime).version==model.version
        results[name]=dict(model_version=model.version,training_report=model.training_report,checkpoint_sha256=sha(out/f'adaptation/model/{name}.json'))
    chosen=rows[:16];base=revise(frozen,chosen,runtime,name='dependence-base',out=out/'dependence')
    duplicate=revise(frozen,chosen+chosen,runtime,name='dependence-duplicates',out=out/'dependence')
    transformed=copy.deepcopy(chosen)
    for row in transformed:
        ancestor=row['dependence_group'];row['dependence_group']=ancestor+'/copy';row['transformation_lineage']=[ancestor,*row['transformation_lineage']]
    correlated=revise(frozen,chosen+transformed,runtime,name='dependence-transformed',out=out/'dependence')
    conflict=copy.deepcopy(chosen[0]);conflict['movement_label']=not conflict['movement_label']
    shared_conflict=revise(frozen,chosen+[conflict],runtime,name='dependence-shared-conflict',out=out/'dependence')
    conflict['dependence_group']='independent-collection-counterexample';conflict['source_game']=conflict['dependence_group'];conflict['transformation_lineage']=[]
    independent_conflict=revise(frozen,chosen+[conflict],runtime,name='dependence-independent-conflict',out=out/'dependence')
    unsafe=revise(frozen,chosen+chosen,runtime,policy='unsafe-row-independent',name='dependence-unsafe',out=out/'dependence')
    game_only=revise(frozen,rows,runtime,policy='game-only',name='dependence-game-only',out=out/'dependence')
    def values(model):return {channel:{k:(h['positive'],h['negative']) for k,h in hypotheses.items()} for channel,hypotheses in [('promotion',model.hypotheses),('local',model.source_model().hypotheses)]}
    assert values(base)==values(duplicate)==values(correlated)
    dependence=dict(duplicate_native_values_equal=True,transformed_ancestor_native_values_equal=True,
        unsafe_counting_changes_values=values(base)!=values(unsafe),
        models={name:dict(version=m.version,report=m.training_report,values=values(m)) for name,m in [('base',base),('duplicates',duplicate),('transformed',correlated),('shared-conflict',shared_conflict),('independent-conflict',independent_conflict),('unsafe',unsafe),('game-only',game_only)]},
        interpretation='Native revision is unchanged. Independence is an external sampling assumption: game clustering alone cannot establish independence of repeated openings; the conservative main policy groups both. Contradictory observations within a game are excluded; independent contradictions revise both native channels.')
    write_json(out/'dependence/summary.json',dependence)
    write_json(out/'adaptation/summary.json',dict(models=results,frozen_model=frozen.version,frozen_evaluation_completed_unix=receipt['completed_unix'],
        training_completed_unix=time.time(),new_learning_promoted=False,small_games=sorted(small),large_games=24,
        final_test_used_for_training=False,thresholds_changed=False,source_data_hash=data['hash']))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
