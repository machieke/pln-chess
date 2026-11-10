"""Describe exact relative-context sharing after the field model is frozen."""
import argparse
import chess
from collections import Counter, defaultdict
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from pln_chess.domain import Position, parse_square
from pln_chess.spatial import oriented, delta, ray_cells
from pln_chess.pln import Runtime
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    assert (out / 'field-evaluation/summary.json').exists(), 'Descriptive audit follows frozen held-out evaluation'
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.ontology import observe_relation
    model = FieldModel.load(out / 'model/C11-field-trained.json', Runtime())
    data = read_gzip(out / 'datasets/field-queries.json.xz')
    seen_keys, raw_contexts, displacements = set(), set(), set()
    support = defaultdict(list)
    counts = defaultdict(Counter)
    positions = {}
    for split in ('train','calibration','test'):
        for row in data['queries']:
            if row['split'] != split:
                continue
            position = positions.setdefault(row['fen'],Position.from_fen(row['fen']))
            piece = position.at(parse_square(row['piece_square']))
            target = parse_square(row['target_square'])
            offset = list(oriented(delta(piece.square,target),piece.owner))
            def occupancy(square):
                other = position.at(square)
                return ['Empty'] if other is None else [other.kind,'friendly' if other.owner==piece.owner else 'opponent']
            for family,label in row['labels'].items():
                if label is None:
                    continue
                observation = observe_relation(position,piece,target,family,source=row['source'])
                key = observation['rule_id']
                # This descriptor audit retains raw displacement and full typed
                # path contents. It deliberately includes more detail than the
                # pooled learned context; it is not a second learned key.
                raw = digest([family,piece.kind,offset,occupancy(target),
                    [[list(oriented(delta(piece.square,s),piece.owner)),occupancy(s)] for s in ray_cells(piece.square,target)],
                    observation['descriptor']])
                displacement = (family,piece.kind,*offset)
                if split == 'train':
                    seen_keys.add(key)
                    raw_contexts.add(raw)
                    displacements.add(displacement)
                    support[key].append(dict(query=row['id'],source=row['source'],group=row['dependence_group'],
                        ancestry=row['transformation_lineage'],relative_displacement=offset,raw_context=raw,label=label))
                else:
                    counter = counts[split+'/'+family]
                    counter['relations'] += 1
                    counter['pooled_key_observed_in_training'] += key in seen_keys
                    counter['conditional_present_in_checkpoint'] += key in model.hypotheses
                    counter['raw_relative_context_observed_in_training'] += raw in raw_contexts
                    counter['raw_displacement_observed_in_training'] += displacement in displacements
    dedicated = []
    for case in read_json(out/'datasets/worked-controls.json')['transfers']:
        position = Position.from_fen(case['fen'])
        piece = position.at(parse_square(case['source']))
        observation = observe_relation(position,piece,parse_square(case['target']),case['field'],source='dedicated-audit')
        examples = support.get(observation['rule_id'],[])
        dedicated.append(dict(case=case,descriptor=observation['descriptor'],rule_id=observation['rule_id'],
            matched_training_queries=len(examples),training_displacements=sorted({tuple(e['relative_displacement']) for e in examples}),
            training_groups=sorted({e['group'] for e in examples}),training_examples=examples,
            learned_evidence_ids=model.hypotheses.get(observation['rule_id'],{}).get('evidence_ids',[]),
            raw_displacement_seen=(case['field'],piece.kind,*observation['relative_displacement']) in displacements))
    assert all(not row['raw_displacement_seen'] for row in dedicated)
    conflicts = {key:dict(labels=dict(Counter(str(e['label']) for e in examples)),groups=sorted({e['group'] for e in examples}))
        for key,examples in support.items() if len({e['label'] for e in examples}) > 1}
    pack(out/'field-learning/relative-sharing.json.xz',dict(dedicated_transfers=dedicated,training_label_conflicts=conflicts))
    write_json(out/'field-learning/relative-sharing-summary.json',dict(passed=True,model_version=model.version,
        dataset_hash=data['hash'],counts={name:dict(values) for name,values in counts.items()},
        training_observed_keys=len(seen_keys),training_raw_relative_contexts=len(raw_contexts),
        training_conflicting_pooled_keys=len(conflicts),dedicated_transfers=len(dedicated),all_dedicated_displacements_unseen=True,
        model_or_thresholds_changed=False,
        scope='Post-freeze descriptive audit. Shared relative categories are the intended supplied abstraction; unseen raw distances do not establish independently learned shape pooling. Full-board/ancestry independence is checked separately.'))
    # Preserve the registered primary labels/results. The reference API accepts
    # king-to-rook castling aliases, beyond the two-cell castle excluded by the
    # original ordinary-mobility label adapter. Describe that mismatch after
    # freezing; do not tune the model or rewrite the original denominator.
    queries={row['id']:row for row in data['queries']}
    rows=read_gzip(out/'field-evaluation/rows.json.xz')
    errors=[]
    for row in rows:
        if row['arm']!='trained' or row['split']!='test' or not row['label'] or row['classification']!='contradicted':
            continue
        query=queries[row['query']]
        board=chess.Board(query['fen'])
        source,target=chess.parse_square(query['piece_square']),chess.parse_square(query['target_square'])
        piece=board.piece_at(source)
        board.turn=piece.color
        move=chess.Move(source,target)
        errors.append(dict(result=row,query=query,hypothesis=model.hypotheses[row['rule_id']],
            reference_castling_alias=board.is_castling(move),reference_pseudo_legal=board.is_pseudo_legal(move)))
    write_json(out/'field-evaluation/post-freeze-false-negatives.json',dict(errors=errors,count=len(errors),
        castling_alias_count=sum(e['reference_castling_alias'] for e in errors),model_changed=False,threshold_changed=False,
        frozen_primary_labels_changed=False,ordinary_mobility_label_adapter_gap='King-to-rook castling aliases were not excluded by the two-cell castle filter.',
        scope='Descriptive held-out failure audit only. All nine primary mobility false negatives remain in the registered metrics; no retraining, label replacement or performance claim based on post-hoc exclusions.'))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
