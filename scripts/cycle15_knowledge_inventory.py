"""Document every supplied template without changing its native encoding."""
from pln_chess.common import ROOT,write_json
from research.cycle15.knowledge import templates
from research.cycle15.native_reasoner import parse,render
from training.cycle15_consequences import LEARNED


def run():
    scope={
        'empty-tail':'Empty list initialization; does not assert an observed ray is clear',
        'extend-empty':'One use in a derivation; a second recursive use overlaps the same rule stamp',
        'clear-path':'Connects a supplied structural ray to a natively supported empty path; longer empty paths remain unsupported',
        'clear-one':'Exactly one observed empty intermediate cell; no arbitrary-ray claim',
        'rook-attack':'Orthogonal sliding influence given supported clearance; one-cell positive pilot/development evidence',
        'bishop-attack':'Diagonal sliding influence given supported clearance; one-cell held-out positive evidence',
        'queen-orthogonal':'Orthogonal sliding influence given supported clearance; one-cell held-out positive evidence',
        'queen-diagonal':'Diagonal sliding influence given supported clearance; one-cell held-out positive evidence',
        'obstruction':'Specified occupied intervening cell; held-out negative endpoints cover ray lengths 2 through 7',
        'exposure-white':'White actor, white king target and black attacker, with same-state attack support; no full move-legality conclusion',
        'exposure-black':'Symmetric supplied template; not an independent black-actor final-test estimate',
    }
    rows={}
    for name,term in templates().items():
        node=parse(term);premises=[]
        while isinstance(node,list) and node[0]=='Implication':
            premises.append(render(node[1]));node=node[2]
        rows[name]=dict(term=term,origin='supplied-domain-rule-template',required_premises=premises,
            intended_conclusion=render(node),learned_parameters=['strength','confidence'] if name in LEARNED else [],
            evidence_source='Registered training root conditional observations, native revision and ancestry ledger'
                if name in LEARNED else 'Supplied domain hypothesis with disclosed (stv 1.0 0.95) assumption',
            dependence_assumptions='Stable rule stamp per template; learned templates also retain admitted root ancestry; atomic sensor occurrences from one state are not claimed statistically independent',
            supported_and_unsupported_scope=scope[name],logical_structure_learned=False,
            native_calculus_changed=False)
    assert len(rows)==11
    write_json(ROOT/'knowledge/cycle15/schemas.json',rows)


if __name__=='__main__':run()
