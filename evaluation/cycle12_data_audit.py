"""Independent partition, ancestry and reference integrity checks."""
import argparse
from collections import defaultdict
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from training.cycle12_data import canonical_motif, reference
from training.cycle12_controls import transform
from pln_chess.domain import Position
from pln_chess.api import find_move


def run(out):
    out=Path(out);data=read_json(out/'datasets/concepts.json')
    expected=data.pop('hash');assert digest(data)==expected;data['hash']=expected
    by_family=defaultdict(set);raw=defaultdict(set);names=defaultdict(list)
    for row in data['records']:
        assert row['input']['concept'] in data['targets']
        assert not any(k in row['input'] for k in ('label','reference','expected','proof','score'))
        assert reference(row['input'])==row['reference'],row['id']
        if row['input']['move']:
            assert find_move(Position.from_fen(row['input']['fen']),row['input']['move']) is not None,row['id']
        by_family[row['structural_family']].add(row['split'])
        key=canonical_motif(row['input'])
        raw[key].add(row['split']);names[key].append(row['id'])
        assert row['dependence_group']==row['structural_family']
        assert row['transformation_lineage']==[row['structural_family']]
    overlap=[dict(splits=sorted(splits),examples=names[key]) for key,splits in raw.items() if len(splits)>1]
    assert all(len(splits)==1 for splits in by_family.values())
    assert not overlap,overlap
    symmetry=[]
    for row in data['records']:
        if row['variant']!='base':continue
        if row['input']['concept']=='TrappedPiece':
            # Pawns surrounding a non-pawn subject have movement-independent
            # occupancy roles, but color orientation reverses all ownership.
            operations=('reflection','identity-renaming')
        else:operations=('translation','reflection','color-orientation','identity-renaming')
        for operation in operations:
            other=transform(row['input'],operation)
            if other is None:continue
            assert canonical_motif(other)==canonical_motif(row['input']),(row['id'],operation)
            symmetry.append(dict(case=row['id'],operation=operation,canonical_family_preserved=True))
    controls=read_json(out/'datasets/concept-controls.json')
    assert controls['dataset_hash']==data['hash']
    for row in controls['transformations']:
        assert row['dependence_group'] in by_family
        assert by_family[row['dependence_group']]=={'test'}
        assert row['independent_holdout'] is False
    sequences=read_json(out/'datasets/sequences.json')
    assert len(sequences['sequences'])>=10
    event_ids=[]
    for sequence in sequences['sequences']:
        supplied=sequence['input']
        assert 'reference' not in supplied and all('reference' not in event for event in supplied['events'])
        event_ids.extend(event['id'] for event in supplied['events'])
        assert sequence['reference']['all_moves_legal']
    assert len(set(event_ids))==len(event_ids)
    result=dict(passed=True,dataset_hash=expected,records=len(data['records']),families=len(by_family),
        partition_family_overlap=[],raw_equivalent_motif_overlap=overlap,symmetry_checks=symmetry,
        sequences=len(sequences['sequences']),unique_sequence_events=len(event_ids),
        inputs_exclude_reference_labels=True,
        conditional_key_overlap='Measured after observation grammar freeze and training. Supplied pooling may intentionally share keys across different raw families.',
        independence_limit='One controlled synthetic source. Distinct raw role topology/distance families are split; these are not independent external chess studies. Equivalent transformations and counterfactual descendants never count as extra holdouts.',
        preregistration_revision='Drafts are retained under datasets/pre-audit-registration and pre-move-grammar-audit. Before fitting, symmetric role permutations and trapping boundary topology were added to the family audit; one-cell orthogonal vacating/interposing edits use rook movers so every proposed edit belongs to the structural movement grammar. Counts, split assignments and limited-target labels did not change.')
    write_json(out/'datasets/audit.json',result)
    print('Concept data audit passed',len(data['records']),len(by_family),len(symmetry),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
