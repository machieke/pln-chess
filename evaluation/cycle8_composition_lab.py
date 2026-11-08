"""Isolated exact arithmetic research. Never imported by production inference.

These probability bounds are proposed richer semantics, NOT native PLN STVs.
An STV has no automatic lift to a calibrated probability interval.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
from pln_chess.common import ROOT, digest, write_json


@dataclass(frozen=True)
class Bounds:
    lower: F
    upper: F

    def __post_init__(self):
        object.__setattr__(self, 'lower', F(self.lower))
        object.__setattr__(self, 'upper', F(self.upper))
        if not 0 <= self.lower <= self.upper <= 1:
            raise ValueError('Invalid probability interval')

    def json(self):
        return {'lower': str(self.lower), 'upper': str(self.upper),
                'decimal_lower': float(self.lower), 'decimal_upper': float(self.upper)}


UNKNOWN = Bounds(0, 1)


def frechet(a, b):
    return Bounds(max(F(0), a.lower + b.lower - 1), min(a.upper, b.upper))


def intersection(a, b):
    """Constraint conjunction; conflicting assessments are NOT averaged."""
    return Bounds(max(a.lower, b.lower), min(a.upper, b.upper))


def independent(a, b, certificate):
    if certificate.get('kind') != 'population-event-factorization' or not certificate.get('assumption_id'):
        raise ValueError('Explicit event-independence assumption required')
    return Bounds(a.lower*b.lower, a.upper*b.upper)


def consequent(joint, given_joint=None, given_complement=None):
    """Total probability under independently specified conditional constraints."""
    if given_joint is None:
        return UNKNOWN
    other = given_complement or UNKNOWN
    values = [q*r + (1-q)*t for q,r,t in product(
        (joint.lower,joint.upper), (given_joint.lower,given_joint.upper), (other.lower,other.upper))]
    return Bounds(min(values), max(values))


def coverage(certificates):
    """Union bound on validity certificates; no STV confidence conversion."""
    by_id = {}
    for certificate in certificates:
        key = certificate['id']
        if key in by_id and by_id[key] != certificate:
            raise ValueError('Conflicting certificate under the same immutable ID')
        by_id[key] = certificate
    if not by_id or any(c.get('alpha') is None for c in by_id.values()):
        return None
    alphas = [F(c['alpha']) for c in by_id.values()]
    if any(not 0 <= a <= 1 for a in alphas):
        raise ValueError('Invalid certificate error budget')
    return max(F(0), 1-sum(alphas))


def joint_cells(a, b, x):
    """A,B marginals and proposed intersection define all four masses."""
    cells = (1-a-b+x, b-x, a-x, x)  # 00,01,10,11
    if any(c < 0 for c in cells) or sum(cells) != 1:
        raise ValueError('Incoherent joint table')
    return cells


def check_mathematics():
    grids = 0; tables = 0
    for ai,bi in product(range(21), repeat=2):
        a,b = F(ai,20),F(bi,20); bound=frechet(Bounds(a,a),Bounds(b,b))
        # Analytic extreme tables attain both claimed bounds exactly.
        for x in (bound.lower,bound.upper):
            cells=joint_cells(a,b,x); assert cells[2]+cells[3]==a and cells[1]+cells[3]==b
            assert min(cells)>=0 and sum(cells)==1; tables+=1
        assert bound == frechet(Bounds(b,b),Bounds(a,a))
        assert bound.lower<=a*b<=bound.upper;grids+=1
    # Check interval propagation contains all corners of admissible marginals.
    intervals=[Bounds(F(a,4),F(b,4)) for a in range(5) for b in range(a,5)]
    interval_cases=0
    for a,b in product(intervals,repeat=2):
        bound=frechet(a,b)
        for aa,bb in product((a.lower,a.upper),(b.lower,b.upper)):
            corner=frechet(Bounds(aa,aa),Bounds(bb,bb))
            assert bound.lower<=corner.lower<=corner.upper<=bound.upper
        interval_cases+=1
    # Pairwise independent triples are not mutually independent.
    even={w:F(1,4) if sum(w)%2==0 else F(0) for w in product((0,1),repeat=3)}
    odd={w:F(1,4) if sum(w)%2==1 else F(0) for w in product((0,1),repeat=3)}
    for table in (even,odd):
        for i in range(3):assert sum(p for w,p in table.items() if w[i])==F(1,2)
        for i,j in ((0,1),(0,2),(1,2)):assert sum(p for w,p in table.items() if w[i] and w[j])==F(1,4)
        # Logical grouping is associative on a retained full joint model.
        assert sum(p for w,p in table.items() if (w[0] and w[1]) and w[2])==sum(p for w,p in table.items() if w[0] and (w[1] and w[2]))
    a={'id':'measurement-A','alpha':'1/20'};b={'id':'measurement-B','alpha':'1/10'}
    assert coverage([a,a])==coverage([a])==F(19,20)
    assert coverage([a,b])==coverage([b,a])==F(17,20)
    assert coverage([]) is None and coverage([{'id':'uncalibrated','alpha':None}]) is None
    assert consequent(Bounds(F(2,5),F(3,5)))==UNKNOWN
    assert consequent(Bounds(F(1,2),F(1,2)),Bounds(1,1))==Bounds(F(1,2),1)
    try:intersection(Bounds(F(4,5),1),Bounds(0,F(1,5)))
    except ValueError:conflict=True
    else:raise AssertionError('Inconsistent constraints were accepted')
    return {'passed':True,'exact_marginal_pairs':grids,'attaining_joint_tables':tables,
        'interval_pairs':interval_cases,'duplicate_certificate_idempotence':True,'inconsistent_constraints_rejected':conflict,
        'pairwise_not_mutual_counterexample':{'even_parity_P111':str(even[(1,1,1)]),'odd_parity_P111':str(odd[(1,1,1)]),
            'naive_pairwise_product_P111':'1/8','all_marginals':'1/2','all_pairwise_intersections':'1/4'},
        'scope':'Exact finite arithmetic checks supplement the analytic proofs; they do not validate empirical independence or STV calibration.'}


def run(out):
    from evaluation.cycle7_native import Recorder, probe, learned_premises
    out=Path(out);rt=Recorder();learned,ledger=learned_premises(rt)
    # Reexecute known pinned operators, not another search for encodings.
    a,b=[learned[k].metta() for k in ('A','B')]
    native=[]
    for name,expr in {
        'independent-premises':f'(PLN.Query ((Sentence (A {a}) (source-A)) (Sentence (B {b}) (source-B))) C 12 30 60)',
        'supplied-conditional':f'(PLN.Query ((Sentence (A {a}) (source-A)) (Sentence (B {b}) (source-B)) (Sentence ((Implication A (Implication B C)) (stv 0.95 0.8)) (supplied-rule))) C 12 30 60)',
        'unknown-B':f'(PLN.Query ((Sentence (A {a}) (source-A)) (Sentence (B (stv 0.5 0.0)) (source-B)) (Sentence ((Implication A (Implication B C)) (stv 0.95 0.8)) (supplied-rule))) C 12 30 60)',
        'shared-evidence':f'(PLN.Query ((Sentence (A {a}) (shared)) (Sentence (B {b}) (shared)) (Sentence ((Implication A (Implication B C)) (stv 0.95 0.8)) (supplied-rule))) C 12 30 60)',
        'native-duplicate-revision':f'(Truth_Revision {a} {a})',
        'native-conflicting-revision':f'(Truth_Revision {a} (stv 0.0 0.8))',
        'native-negation':f'(Truth_Negation {a})',
    }.items():
        families={'A','B'} if name in ('independent-premises','supplied-conditional','shared-evidence') else {'A'}
        ids=[r['evidence_id'] for r in ledger if r['family'] in families]
        groups=[r['source_group'] for r in ledger if r['family'] in families]
        if name in ('supplied-conditional','unknown-B','shared-evidence'):
            ids.append(digest(['supplied-conditional',.95,.8]));groups.append('supplied-conditional')
        if name=='native-conflicting-revision':
            ids.append(digest(['supplied-counterobservation',0,.8]));groups.append('supplied-counterobservation')
        record=probe(rt,name,expr)
        if name in ('native-negation','native-duplicate-revision','native-conflicting-revision','supplied-conditional'):
            assert len(record['stvs'])==1,(name,record['result'])
        else:
            assert not record['stvs'] and record['result'].endswith(' ())'),(name,record['result'])
        native.append({**record,'proof_status':'native-partial-proof' if record['stvs'] else 'unknown-conclusion',
            'native_complete_positive_proof':False,'runtime_version':rt.version,'model_version':'C8-existing-native-controls-v1',
            'premise_ids':sorted(families),'evidence_ids':ids,'dependence_groups':groups,
            'rule_ids':['PLN.Query'] if 'PLN.Query' in expr else [expr.split()[0][1:]],
            'derivation_order':sorted(families)+[name],
            'budget':{'query_steps':12,'query_attempts':30,'query_depth':60}})
    certificate={'kind':'population-event-factorization','assumption_id':'toy-generated-independent-Bernoulli-population'}
    def rec(name,expression,result,premises,**extra):
        evidence=[digest(['C8-lab',p]) for p in premises]
        return {'id':name,'expression':expression,'result':result.json(),'premise_ids':premises,
            'evidence_ids':evidence,'dependence_groups':premises,'rule_id':'proposed-credal-joint-v1',
            'proof_status':'proposed-rule-experimental-result','native':False,'runtime_version':rt.version,
            'model_version':'isolated-mathematical-spec-v1','derivation_order':premises+[name],
            'native_stv':None,'confidence':None,'budget':{'max_atoms':3,'arithmetic':'exact rational'},**extra}
    records=[
        rec('independent-positive','IndependentJoint([4/5,4/5],[3/5,3/5],certificate)',independent(Bounds(F(4,5),F(4,5)),Bounds(F(3,5),F(3,5)),certificate),['A','B'],assumption=certificate,without_assumption=frechet(Bounds(F(4,5),F(4,5)),Bounds(F(3,5),F(3,5))).json()),
        rec('positive-negative','Frechet([9/10,9/10],[1/10,1/10])',frechet(Bounds(F(9,10),F(9,10)),Bounds(F(1,10),F(1,10))),['A-positive','B-negative']),
        rec('unknown-premise','Frechet([4/5,4/5],[0,1])',frechet(Bounds(F(4,5),F(4,5)),UNKNOWN),['A','B-unknown'],support_status='unknown'),
        rec('correlated','Joint(P(A)=4/5, B=A)',Bounds(F(4,5),F(4,5)),['A','B-same-event'],naive_product='16/25',dependence='identity, not independence'),
        rec('duplicate','And(A,A) = A',Bounds(F(4,5),F(4,5)),['A'],input_ids=['A','A'],confidence_certificate={'before':'19/20','after':'19/20','meaning':'coverage lower bound, not native STV confidence'}),
        rec('contradiction','And(A,Not(A))',Bounds(0,0),['A','not-A'],inconsistent_assessment='P(A)>=4/5 and P(A)<=1/5 returns InconsistentConstraints, not this zero probability'),
        rec('heldout-conclusion','C from A,B without any relation to C',UNKNOWN,['A','B'],support_status='unsupported-inference',with_supplied_conditionals=consequent(Bounds(F(12,25),F(12,25)),Bounds(F(9,10),F(9,10)),Bounds(F(1,10),F(1,10))).json()),
        rec('chess-relative','Lift learned knight geometry and destination STVs without calibration',UNKNOWN,['knight-relative-geometry','opponent-destination'],support_status='unknown',native_premises={k:v.json() for k,v in learned.items()},fen='2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1',move='f6h5',reason='No approved STV-to-interval calibration or eligibility implication; no complete native proof'),
    ]
    math=check_mathematics()
    write_json(out/'laboratory.json',{'records':records,'native_controls':native,'premise_training':ledger,
        'premise_training_scope':'Pinned C7 synthetic marginal curriculum reexecuted independently; disjoint source groups do not establish statistical independence.',
        'runtime':rt.manifest,'mathematical_checks':math,'production_operator_enabled':False,
        'native_positive_composition':'not demonstrated','assumptions_remaining':['Population transport','Calibrated marginal probability bounds','A learned relation from the joint proposition to the desired consequent']})
    write_json(out/'mathematical-validation.json',math);write_json(out/'native-transcripts.json',rt.transcripts)
    for i,t in enumerate(rt.transcripts):
        p=out/f'native-{i:02}.metta';p.write_text('!(import! &self "'+str(rt.library)+'")\n'+t['body']+'\n')
    return math


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
