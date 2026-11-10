"""Measured interaction graphs, actual sequences and exact incremental parity."""
import argparse
import copy
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position, Piece
from pln_chess.pln import Runtime
from evaluation.cycle7_io import pack
from evaluation.cycle11_fields import metrics


def reference_rows(field,reference):
    labels={(r['source'],r['target']):r['labels'] for r in reference};result=[]
    for r in field['relations']:
        expected=labels[(r['source_square'],r['target_square'])].get(r['family'])
        if expected is None:continue
        result.append(dict(family=r['family'],label=expected,classification=r['classification'],truth_value=r['raw_stv'],
            conditional_proof_complete=r['conditional_proof_complete'],proof_id=r['proof_id'],
            source=r['source_square'],target=r['target_square']))
    return result


def summary_metrics(rows):
    result={}
    for family in ('attack','defense','mobility','king-exposure'):
        selected=[r for r in rows if r['family']==family];value=metrics(selected)
        tp=value['true_positive'];fp=value['false_positive'];positives=value['positives']
        value['f1_including_abstention']=2*tp/(tp+fp+positives) if tp+fp+positives else None
        value['false_positive_rate']=fp/value['negatives'] if value['negatives'] else None
        value['false_negative_rate_supported_only']=value['false_negative']/positives if positives else None
        result[family]=value
    return result


def run(out):
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, build_field, infer_queries, FieldSession
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle12.api import inspect_interactions
    from pln_chess.cycle12.graph import build_graph, validate_graph
    from pln_chess.cycle12.temporal import replay_fields, semantic_replay
    from pln_chess.cycle12.ontology import structural_successor
    from training.cycle12_sequences import field_reference
    import chess
    out=Path(out);assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    data=read_json(out/'datasets/sequences.json');runtime=Runtime(timeout=600);options=FieldOptions(timeout_seconds=600)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    concept=ConceptModel.load(out/'model/C12-concept-trained.json',runtime)
    interactions=list(data['interactions'])
    for name,fen,move in [('knight-opens-rook-file','6k1/8/8/8/8/8/6N1/1K4R1 w - - 0 1','g2f4'),
                          ('pawn-opens-bishop-attack','6k1/7r/8/8/4P3/3B4/8/1K6 w - - 0 1','e4e5')]:
        board=chess.Board(fen);assert board.is_valid() and chess.Move.from_uci(move) in board.legal_moves
        before=field_reference(board);board.push_uci(move)
        interactions.append(dict(input=dict(id=name,fen=fen,move=move),reference=dict(before=before,after=field_reference(board),
            legal=True,after_fen=board.fen(en_passant='fen')),ancestry='additional-development-demo/'+name,
            use='Additional development demonstration, excluded from independent holdout metrics and training.'))
    worked=[];field_rows=[];changes=Counter();reuses=[]
    for case in interactions:
        inp=case['input'];position=Position.from_fen(inp['fen'],unknown_squares=inp.get('unknown_squares',[]))
        source='cycle12-interaction/'+inp['id']
        result=inspect_interactions(position,field,concept,runtime=runtime,options=options,candidate=inp['move'],source=source,max_candidates=16)
        full=build_field(structural_successor(position,inp['move']),field,runtime=runtime,options=options,source=source)
        assert result['after']['fen']==case['reference']['after_fen']
        assert result['after']['relations']==full['relations'] and result['after']['projection']==full['projection']
        assert build_graph(result['after'])==build_graph(full)
        assert not result['execution']['truncated'] and validate_graph(result['graph'])
        rows=reference_rows(result['before'],case['reference']['before'])+reference_rows(result['after'],case['reference']['after'])
        field_rows.extend(rows);changes.update(c['predicate'] for c in result['changes'])
        path='interactions/'+inp['id']+'.json.xz';pack(out/path,dict(case=case,result=result,reference_rows=rows,
            incremental_full_exact=True,full_relation_digest=digest(full['relations'])))
        worked.append(dict(id=inp['id'],artifact=path,relations=len(rows),changes=len(result['changes']),
            concepts=len(result['concepts']),incremental=result['after']['incremental']))
        reuses.append(result['after']['incremental']);print('Interaction',inp['id'],'exact',flush=True)
    write_json(out/'interactions/summary.json',dict(worked=worked,count=len(worked),change_predicates=dict(changes),
        endpoint_field_metrics=summary_metrics(field_rows),incremental_full_exact=True,
        failures=[r for r in field_rows if (r['label'] and r['classification']=='contradicted') or (not r['label'] and r['classification']=='supported')],
        scope='Development examples. Endpoint field metrics do not measure native temporal implication or strategic accuracy.'))

    # The original field metamorphic controls are rerun under the current implementation.
    transformations=[]
    for case in read_json(ROOT/'artifacts/cycle11/datasets/worked-controls.json')['transformations']:
        a=Position.from_fen(case['before_fen']);b=Position.from_fen(case['after_fen'],unknown_squares=case.get('unknown_squares',[]))
        if 'before_pieces' in case:
            a=replace(a,pieces=tuple(Piece(**p) for p in case['before_pieces']));b=replace(b,pieces=tuple(Piece(**p) for p in case['after_pieces']))
        def query(p,side):return infer_queries([dict(id='metamorphic',position=p,source_square=case[side+'_source'],
            target_square=case[side+'_target'],families=[case['field']],source=case['dependence_group'])],field,options,runtime,FieldSession(runtime))['relations'][0]
        before=query(a,'before');after=query(b,'after');same=before['raw_stv']==after['raw_stv'] and before['classification']==after['classification']
        expected=case['expectation'];passed=same and before['rule_id']==after['rule_id'] if expected=='invariant-relative-conditional' else after['classification']=='unknown' if expected=='unknown-required-observation' else before['classification']=='supported' and after['classification']=='contradicted'
        transformations.append(dict(case=case,before=before,after=after,passed=passed))
    pack(out/'interactions/transformations.json.xz',transformations)
    write_json(out/'interactions/transformation-summary.json',dict(cases=len(transformations),passed=sum(r['passed'] for r in transformations),failures=[r['case']['id'] for r in transformations if not r['passed']]))

    sequences=[];temporal_rows=[];parity=[]
    for case in data['sequences']:
        supplied=case['input'];result=replay_fields(supplied,field,concept_model=concept,runtime=runtime,options=options,max_candidates=12)
        semantic=digest(semantic_replay(result));assert result['complete_history'] and not result['execution']['truncated']
        rows=[]
        for state,reference in zip(result['states'],case['reference']['frames'],strict=True):
            observed=state['field'];assert observed['fen']==reference['fen'];assert validate_graph(state['graph'])
            position=replace(Position.from_fen(observed['fen'],unknown_squares=observed['unknown_squares']),pieces=tuple(Piece(**p) for p in observed['pieces']))
            full=build_field(position,field,runtime=runtime,options=replace(options,sensor_confidence=state['observation_confidence']),source=observed['provenance']['source'])
            assert full['relations']==observed['relations'] and full['projection']==observed['projection']
            assert build_graph(full)==build_graph(observed)
            parity.append(dict(sequence=supplied['id'],step=state['step'],exact=True,relations=len(full['relations']),
                relation_digest=digest(full['relations']),incremental=observed['incremental']))
            rows.extend(reference_rows(observed,reference['field_reference']))
        temporal_rows.extend(rows);path='temporal/'+supplied['id']+'.json.xz'
        pack(out/path,dict(case=case,result=result,reference_rows=rows,semantic_hash=semantic))
        del result
        repeated=replay_fields(supplied,field,concept_model=concept,runtime=runtime,options=options,max_candidates=12)
        assert digest(semantic_replay(repeated))==semantic
        sequences.append(dict(id=supplied['id'],states=len(repeated['states']),events=len(supplied['events']),artifact=path,
            deterministic_replay=True,semantic_hash=semantic,complete_history=repeated['complete_history'],
            native_temporal_theorems=0,partial_concept_records=sum(len(s['concepts']) for s in repeated['states'])))
        del repeated;print('Sequence',supplied['id'],'replay and full parity passed',flush=True)
    partial=next(r['input'] for r in data['sequences'] if r['input']['id']=='promotion-threat');gaps=[]
    for name in ('missing-event-observed-state','missing-event-unknown-state','conflicting-successor','zero-confidence'):
        supplied=copy.deepcopy(partial)
        if name.startswith('missing'):
            supplied['events'][1]['move']=None
            if name=='missing-event-unknown-state':supplied['events'][1].pop('observed_fen')
        elif name=='conflicting-successor':supplied['events'][0]['observed_fen']=supplied['initial_fen']
        else:supplied['events'][0]['confidence']=0
        result=replay_fields(supplied,field,runtime=runtime,options=options)
        passed=all(r['classification']=='unknown' for r in result['states'][1]['field']['relations']) if name=='zero-confidence' else not result['complete_history'] and any(t['status']==name and not t['changes'] for t in result['transitions'])
        assert passed;pack(out/f'temporal/controls/{name}.json.xz',dict(input=supplied,result=result,passed=passed));gaps.append(dict(id=name,passed=passed))
    write_json(out/'temporal/summary.json',dict(sequences=sequences,sequence_count=len(sequences),states=len(parity),
        supplied_moves=sum(s['events'] for s in sequences),endpoint_field_metrics=summary_metrics(temporal_rows),
        failures=[r for r in temporal_rows if (r['label'] and r['classification']=='contradicted') or (not r['label'] and r['classification']=='supported')],
        gap_controls=gaps,all_replays_exact=True,planned_moves=False,native_temporal_theorems=0,
        scope='Metrics evaluate separately inferred endpoint fields along fixed observed sequences, not forecasting, search, or strategic sequence selection.'))
    write_json(out/'incremental/parity.json',dict(passed=True,interaction_positions=len(worked),sequence_states=len(parity),states=parity,
        equality='Every relation dictionary, native proof node, evidence/group ID, projection and dependency graph matches independent full recomputation.',
        reused_relations=sum(s['incremental']['reused_relations'] for s in parity)+sum(s['reused_relations'] for s in reuses),
        scheduled_relations=sum(s['incremental']['scheduled_relations'] for s in parity)+sum(s['scheduled_relations'] for s in reuses)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
