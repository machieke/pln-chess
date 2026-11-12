"""Native long-range field controls at the role-projection boundary."""
from dataclasses import asdict,replace
from pathlib import Path

from pln_chess.common import ROOT,digest
from pln_chess.domain import Position,Piece,square_name,parse_square
from pln_chess.spatial import translate,reflect_files,color_flip
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle11.fields.inference import FieldOptions,FieldSession,infer_queries
from pln_chess.cycle14.ontology import role_profile
from training.cycle14_labels import atomic_json
from evaluation.cycle7_io import pack


def run(out='artifacts/cycle14'):
    out=Path(out);runtime=Runtime();model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    # Seven-square ray is deliberately longer than a small local neighborhood.
    original=Position.from_fen('7k/8/8/8/R6p/8/8/6K1 w - - 0 1')
    small=Position.from_fen('8/6k1/8/8/1R3p2/8/6K1/8 w - - 0 1')
    def query(position,source='a4',target='h4',session=None):
        rows=infer_queries([dict(id='c14-locality',position=position,source_square=source,target_square=target,
            families=['attack'],source='cycle14-controlled-locality')],model,FieldOptions(),runtime,session or FieldSession(runtime))
        state={'field':dict(relations=rows['relations'],pieces=[asdict(p) for p in position.pieces],unknown_squares=[list(s) for s in position.unknown_squares])}
        return dict(result=rows,role=role_profile(state,position.at(parse_square(source)).id)['mover-attack'])
    cases=[dict(name='piece-id-renaming',before=original,after=replace(original,pieces=tuple(replace(p,id='renamed-'+p.id) for p in original.pieces)),a=('a4','h4'),b=('a4','h4'),expected='same'),
        dict(name='owner-relative-reversal',before=original,after=color_flip(original),a=('a4','h4'),b=('a5','h5'),expected='same'),
        dict(name='file-reflection',before=original,after=reflect_files(original),a=('a4','h4'),b=('h4','a4'),expected='same'),
        dict(name='translation-with-preserved-ray',before=small,after=translate(small,(1,0)),a=('b4','f4'),b=('c4','g4'),expected='same'),
        dict(name='irrelevant-piece',before=original,after=replace(original,pieces=original.pieces+(Piece('distant','Bishop','Black',(1,6)),)),a=('a4','h4'),b=('a4','h4'),expected='same'),
        dict(name='distant-relevant-blocker',before=original,after=replace(original,pieces=original.pieces+(Piece('far-blocker','Knight','White',(6,3)),)),a=('a4','h4'),b=('a4','h4'),expected='contradicted'),
        dict(name='unknown-distant-ray-cell',before=original,after=replace(original,unknown_squares=frozenset([(6,3)])),a=('a4','h4'),b=('a4','h4'),expected='unknown')]
    results=[]
    for case in cases:
        session=FieldSession(runtime);before=query(case['before'],*case['a'],session=session);after=query(case['after'],*case['b'],session=session);fresh=query(case['after'],*case['b'])
        a,b=before['result']['relations'][0],after['result']['relations'][0]
        equal=a['rule_id']==b['rule_id'] and a['raw_stv']==b['raw_stv'] and before['role']==after['role']
        passed=equal if case['expected']=='same' else b['classification']==case['expected']
        assert after['result']['relations']==fresh['result']['relations']
        results.append(dict(name=case['name'],expected=case['expected'],passed=passed,before=before,after=after,
            fresh_native_parity=True,ancestry='controlled-locality-panel',empirical_independent_examples=0))
    pack(out/'representation/native-locality.json.xz',results)
    atomic_json(out/'representation/locality-summary.json',dict(passed=all(r['passed'] for r in results),N=len(results),
        failures=[r['name'] for r in results if not r['passed']],longest_tested_ray=7,query_scope='Single native attack relation and corresponding mover-role projection',
        limitation='Invariance of a local dependency does not imply every whole-board aggregate descriptor is invariant to every added piece. All relevant occupied targets and the complete sliding path remain in query scope.'))
    assert all(r['passed'] for r in results)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');run(parser.parse_args().out)
