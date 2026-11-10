"""Offline concept transformations and counterfactual pairs, before fitting."""
import argparse
import copy
from dataclasses import asdict, replace
from pathlib import Path
from pln_chess.common import digest, read_json, write_json
from pln_chess.domain import Position, Piece, parse_square, square_name
from pln_chess.spatial import ray_cells
from training.cycle12_data import reference


def transform(case,operation):
    supplied=copy.deepcopy(case)
    position=Position.from_fen(case['fen'])
    if operation=='translation':
        coordinates=[p.square for p in position.pieces]+[parse_square(s) for s in case['roles'].values()]
        delta=(1,0) if max(s[0] for s in coordinates)<7 else (-1,0) if min(s[0] for s in coordinates)>0 else (0,1)
        if any(not (0<=s[0]+delta[0]<8 and 0<=s[1]+delta[1]<8) for s in coordinates):return None
        spatial=lambda s:(s[0]+delta[0],s[1]+delta[1])
    elif operation=='reflection':spatial=lambda s:(7-s[0],s[1])
    elif operation=='color-orientation':spatial=lambda s:(s[0],7-s[1])
    else:spatial=lambda s:s
    pieces=[]
    for index,piece in enumerate(position.pieces):
        pieces.append(replace(piece,square=spatial(piece.square),
            owner=('Black' if piece.owner=='White' else 'White') if operation=='color-orientation' else piece.owner,
            id=f'transformed-entity-{index}' if operation=='identity-renaming' else piece.id))
    if operation=='irrelevant-context':
        role_squares=[parse_square(s) for s in case['roles'].values()]
        dependencies=set(role_squares)
        for a in role_squares:
            for b in role_squares:dependencies.update(ray_cells(a,b))
        if case['move']:
            dependencies.add(parse_square(case['move'][:2]));dependencies.add(parse_square(case['move'][2:4]))
        # Trapping observes a whole local movement fan; a distant addition can
        # affect a long ray. This control is registered only for other concepts.
        if case['concept']=='TrappedPiece':return None
        extra=next(((x,y) for y in range(7,-1,-1) for x in range(7,-1,-1)
                    if (x,y) not in dependencies and position.at((x,y)) is None),None)
        if extra is None:return None
        pieces.append(Piece('irrelevant-context-piece','Knight','Black',extra))
    other=replace(position,pieces=tuple(pieces),turn=('Black' if position.turn=='White' else 'White') if operation=='color-orientation' else position.turn)
    supplied['fen']=other.fen()
    supplied['pieces']=[asdict(p) for p in other.pieces]
    supplied['roles']={r:square_name(spatial(parse_square(s))) for r,s in case['roles'].items()}
    if case['move']:
        move=case['move'];a,b=spatial(parse_square(move[:2])),spatial(parse_square(move[2:4]))
        if not all(0<=n<8 for s in (a,b) for n in s):return None
        supplied['move']=square_name(a)+square_name(b)+move[4:]
    return supplied


def generate(out):
    out=Path(out);data=read_json(out/'datasets/concepts.json')
    selected=[]
    for concept in data['targets']:
        selected.extend([r for r in data['records'] if r['split']=='test' and r['input']['concept']==concept and r['variant']=='base'][:2])
    controls=[];counterfactuals=[]
    for row in selected:
        for operation in ('translation','reflection','color-orientation','identity-renaming','irrelevant-context'):
            other=transform(row['input'],operation)
            if other is None:continue
            ref=reference(other)
            # Some local mobility contexts depend on distance from the edge;
            # translations that change that local structure are not invariance.
            if row['input']['concept']=='TrappedPiece' and operation=='translation':continue
            assert row['reference']['label']==ref['label'],(row['id'],operation)
            controls.append(dict(id=row['id']+'/'+operation,operation=operation,before=row['input'],after=other,
                expected='invariant-relative-conditional',reference_before=row['reference'],reference_after=ref,
                dependence_group=row['structural_family'],transformation_lineage=[row['structural_family']],
                independent_holdout=False))
        # Unknown data is an observation intervention, never a negative label.
        role=next(reversed(row['input']['roles']))
        other=copy.deepcopy(row['input']);other['unknown_squares']=[list(parse_square(other['roles'][role]))]
        controls.append(dict(id=row['id']+'/unknown-required-role',operation='unknown-required-role',
            before=row['input'],after=other,expected='unknown',reference_before=row['reference'],reference_after=row['reference'],
            dependence_group=row['structural_family'],transformation_lineage=[row['structural_family']],independent_holdout=False))
        for variant in data['records']:
            if variant['structural_family']==row['structural_family'] and variant['variant']!='base':
                counterfactuals.append(dict(id=variant['id'],before=row['input'],after=variant['input'],
                    reference_before=row['reference'],reference_after=variant['reference'],changed_relation=variant['variant'],
                    dependence_group=row['structural_family'],independent_holdout=False))
    transfers={}
    for concept in ('Pin','Fork'):
        records=[r for r in data['records'] if r['split']=='test' and r['input']['concept']==concept and r['variant']=='base']
        # Retain every fork type, including the genuinely unsupported pawn type.
        chosen=records if concept=='Fork' else records[::max(1,len(records)//8)][:8]
        assert len(chosen)>=5
        transfers[concept]=[dict(id=r['id'],input=r['input'],reference=r['reference'],structural_family=r['structural_family']) for r in chosen]
    payload=dict(schema=12,dataset_hash=data['hash'],transformations=controls,counterfactuals=counterfactuals,
        transfers=transfers,selected_without_model_predictions=True,
        metric_scope='Controls inherit held-out ancestry and are never counted as additional independent samples.')
    payload['hash']=digest(payload)
    write_json(out/'datasets/concept-controls.json',payload)
    print('Registered',len(controls),'transformations/unknown controls,',len(counterfactuals),'counterfactuals, transfers',
          {k:len(v) for k,v in transfers.items()},payload['hash'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    generate(parser.parse_args().out)
