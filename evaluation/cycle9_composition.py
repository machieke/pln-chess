"""New specification counterexamples only; no native operator is implemented."""
import argparse
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import re
from pln_chess.common import ROOT,write_json,read_json
from scripts.cycle9_baseline import sha


def review(out):
    source=ROOT/'vendor/pln/lib_pln.metta';lock=read_json(ROOT/'configs/runtime-lock.json')
    assert sha(source)==lock['pln']['sha256']
    text=source.read_text();operators=sorted(set(re.findall(r'^\(= \(([^\s()]+)',text,re.M)))
    # A= B, C either equal to or disjoint from them. The same exact marginal
    # interval for J=A&B and C cannot retain the dependence needed downstream.
    tables={'same':{'000':F(1,2),'111':F(1,2)},'opposite':{'001':F(1,2),'110':F(1,2)}}
    rows=[]
    for name,t in tables.items():
        marginal=lambda predicate:sum(p for w,p in t.items() if predicate(w))
        row=dict(name=name,table={w:str(p) for w,p in t.items()},
            P_J=str(marginal(lambda w:w[0]==w[1]=='1')),P_C=str(marginal(lambda w:w[2]=='1')),
            P_J_and_C=str(marginal(lambda w:w=='111')))
        assert row['P_J']==row['P_C']=='1/2';rows.append(row)
    assert rows[0]['P_J_and_C']!=rows[1]['P_J_and_C']
    # A valid constraint A=1 plus conditional C|A=.2 and C|not A=.9.
    # Intersecting revised A=0 is inconsistent, whereas replacing A=1 by A=0
    # changes the projected C. Thus revision/replacement cannot be commuted
    # with projection from a cached marginal alone.
    revision=dict(initial_constraints={'P_A':'1','P_C_given_A':'1/5','P_C_given_not_A':'9/10'},
        original_P_C='1/5',replacement_P_A='0',replacement_P_C='9/10',
        intersection_status='InconsistentConstraints',conclusion='Retraction requires retained original constraints and provenance; endpoint-only revision is insufficient.')
    assert F(1)*F(1,5)+(1-F(1))*F(9,10)==F(revision['original_P_C'])
    assert F(0)*F(1,5)+(1-F(0))*F(9,10)==F(revision['replacement_P_C'])
    # Twenty distinct, disjoint certificate failure events each have probability
    # 1/20; all constraints being valid then has probability zero, not .95.
    certificate=dict(individual_alpha='1/20',certificates=20,disjoint_failure_mass=str(20*F(1,20)),
        simultaneous_coverage='0',naive_reuse_of_single_confidence='19/20',
        conclusion='Per-premise confidence is not joint validity, even with no duplicate observation IDs.')
    result=dict(schema=9,native=False,passed=True,runtime_pln=lock['pln'],source_sha256=sha(source),
        source_defined_heads=operators,interval_information_loss=rows,revision_projection_counterexample=revision,
        confidence_counterexample=certificate,prior_evidence={
            'C8_proposal':sha(ROOT/'docs/cycle8/native-composition-proposal.md'),
            'C8_math':sha(ROOT/'artifacts/cycle8/composition/mathematical-validation.json'),
            'C7_native_inventory':sha(ROOT/'artifacts/cycle7/native/inventory.json')},
        repeat_native_experiments=False,new_operator_enabled=False,
        recommendation={'operational':'A: existing native operators',
            'isolated_research':'B justified conditionally as a separate credal type, subject to explicit future authorization and statistical/solver contracts.',
            'production_extension':'NO-GO',
            'representation':'C: learned joint antecedent may be represented with existing conditionals; it does not derive a conjunction from marginal beliefs.'})
    write_json(Path(out)/'composition/review.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);review(p.parse_args().out)
