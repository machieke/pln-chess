"""Independent external limited-concept references, selected before PLN fitting."""
import argparse
from collections import Counter
import copy
import csv
from pathlib import Path

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.cycle12.candidates import enumerate_concepts
from training.cycle12_data import reference, canonical_motif
from training.cycle12_controls import transform

FAMILIES=('Pin','Fork','DiscoveredAttack','DiscoveredDefense','MultipleAttackers',
          'OverloadedDefender','TrappedPiece','ThreatRemoval')
THEMES=dict(Pin='pin',Fork='fork',DiscoveredAttack='discoveredAttack',DiscoveredDefense='defensiveMove',
    MultipleAttackers='attackingF2F7',OverloadedDefender='deflection',TrappedPiece='trappedPiece',ThreatRemoval='defensiveMove')


def run(out):
    out=Path(out);pool=list(csv.DictReader((out/'sources/lichess-puzzle-prefix.csv').open()))
    preference_games={r['source'].get('game_url',r['source_game']).split('#')[0].rstrip('/').removesuffix('/black')
        for r in read_json(out/'datasets/source-pairs.json')['records']}
    old=read_json(ROOT/'artifacts/cycle12/datasets/concepts.json')['records']
    training_families={digest(canonical_motif(r['input'])) for r in old if r['split']=='train'}
    training_families.update(r['structural_family'].split(':',1)[1] for r in old if r['split']=='train')
    rows=[];attempts={};used=set();controls=[];used_families=set();excluded_families=Counter()
    for family in FAMILIES:
        wanted=THEMES[family]
        choices=sorted(pool,key=lambda r:(wanted not in r['Themes'].split(),digest([131313,family,r['PuzzleId']])))
        counts=Counter();inspected=0
        for puzzle in choices:
            if counts[True]>=8 and counts[False]>=4:break
            game=puzzle['GameUrl'].split('#')[0].rstrip('/').removesuffix('/black')
            if game in used or game in preference_games:continue
            moves=puzzle['Moves'].split()
            if len(moves)<2:continue
            board=chess.Board(puzzle['FEN'])
            if not board.is_valid():continue
            board.push_uci(moves[0]);move=moves[1]
            if chess.Move.from_uci(move) not in board.legal_moves:continue
            inspected+=1
            enumeration=enumerate_concepts(board.fen(en_passant='fen'),move=move,concepts=[family],max_candidates=64,
                source='cycle13-external-concept/'+puzzle['PuzzleId'])
            for case in enumeration['candidates']:
                case=copy.deepcopy(case);case.setdefault('move',None)
                if family in ('DiscoveredAttack','DiscoveredDefense','ThreatRemoval'):
                    # The frozen reference target uses stationary endpoint roles.
                    # Do not quietly broaden it to moving-role semantics.
                    if case['roles']['attacker']==case['roles']['mover'] or case['roles']['target']==case['roles']['mover']:continue
                structural=digest(canonical_motif(case))
                if structural in training_families or structural in used_families:
                    excluded_families['training-overlap' if structural in training_families else 'external-duplicate']+=1
                    continue
                ref=reference(case);label=ref['label']
                if counts[label]>=(8 if label else 4):continue
                identifier=f"c13-concept-{family}-{puzzle['PuzzleId']}"
                case['id']=identifier
                row=dict(id=identifier,input=case,reference=ref,source_game=game,
                    source=dict(puzzle_id=puzzle['PuzzleId'],game_url=puzzle['GameUrl'],themes=puzzle['Themes'].split(),
                        puzzle_url='https://lichess.org/training/'+puzzle['PuzzleId']),
                    split='external-test',dependence_group='external-game:'+digest(game),
                    structural_family='external-motif:'+structural,
                    selection='Bounded structural candidates, stratified by independent offline limited-target label; no PLN model prediction used.',
                    enumeration_truncated=enumeration['truncated'])
                rows.append(row);used.add(game);used_families.add(structural);counts[label]+=1
                for operation in ('reflection','color-orientation','identity-renaming'):
                    after=transform(case,operation)
                    if after is None:continue
                    after_reference=reference(after)
                    if after_reference['label']!=label:continue
                    controls.append(dict(id=identifier+'/'+operation,before=case,after=after,
                        reference=ref,expected='invariant',operation=operation,
                        dependence_group=row['dependence_group'],independent_example=False))
                if family=='Fork' and label:
                    for operation in ('remove-target','friendly-target','unknown-target'):
                        after=copy.deepcopy(case);after.pop('pieces',None)
                        square=after['roles']['target_b'];other=chess.Board(after['fen'])
                        if operation=='remove-target':other.remove_piece_at(chess.parse_square(square))
                        elif operation=='friendly-target':
                            piece=other.piece_at(chess.parse_square(square));actor=other.piece_at(chess.parse_square(after['roles']['attacker']))
                            other.set_piece_at(chess.parse_square(square),chess.Piece(piece.piece_type,actor.color))
                        else:after['unknown_squares']=[square]
                        after['fen']=other.fen(en_passant='fen')
                        controls.append(dict(id=identifier+'/'+operation,before=case,after=after,
                            reference=None if operation=='unknown-target' else reference(after),
                            expected='unknown' if operation=='unknown-target' else 'contradicted',operation=operation,
                            dependence_group=row['dependence_group'],independent_example=False))
                break
            if inspected>=3000:break
        attempts[family]=dict(positions_examined=inspected,positive=counts[True],negative=counts[False],
            target_positive=8,target_negative=4,coverage_complete=counts[True]>=8 and counts[False]>=4)
        print('EXTERNAL CONCEPT SOURCE',family,attempts[family],flush=True)
    assert len({r['source_game'] for r in rows})==len(rows)
    assert not {r['source_game'] for r in rows}&preference_games
    assert len(used_families)==len(rows) and not used_families&training_families
    payload=dict(schema='c13-external-concepts-v1',records=rows,controls=controls,selection=attempts,
        independent_games=len(rows),independent_raw_structural_families=len(used_families),
        starting_training_raw_motif_overlap=0,excluded_equivalent_families=dict(excluded_families),
        source='Frozen Lichess puzzle source prefix; source games disjoint from preference corpus, raw motifs disjoint from registered concept training.',
        labels_are_limited_targets=True,complete_strategic_labels=False,selected_before_pln_fitting=True)
    payload['hash']=digest(payload);destination=out/'datasets/external-concepts.json'
    if destination.exists():assert digest(read_json(destination))==digest(payload)
    else:write_json(destination,payload)
    print('EXTERNAL CONCEPT SOURCES',len(rows),'independent cases;',len(controls),'dependent controls',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
