"""Replay unchanged pinned native inputs. No reference mathematics imports."""
from pathlib import Path
from unittest.mock import patch
from pln_chess.common import read_json
from research.cycle15.native_reasoner import NativeReasoner, Sentence, Budgets, save_result
from research.cycle16.evidence_audit import minimal, dependencies
from research.cycle16.records import record
from research.cycle17.provenance import witness
from .contracts import sha
from .source_mapping import ARMS


def run(root,out):
    root=Path(root);out=Path(out);reasoner=NativeReasoner();rows={};receipts=[]
    index=read_json(root/'artifacts/cycle17/witnesses/index.json')
    with patch('chess.Board.attacks',side_effect=AssertionError('Evaluation oracle forbidden during native replay')):
        for arm in (*ARMS,'historical-shared'):
            source=index[arm]['native'];assert sha(root/source['path'])==source['sha256']
            old=read_json(root/source['path']);stages=old.get('stages',{'Attack':old});fresh={};native_stages={}
            for name,stage in stages.items():
                current=reasoner.infer([Sentence(**r) for r in stage['facts']],[Sentence(**r) for r in stage['rules']],
                    stage['query'],contrary=stage['contrary_query'],budgets=Budgets(**stage['budgets']),
                    marginals=stage['marginals'],mode=stage['api'])
                assert not current['incomplete']
                for key in ('answer','contrary','classification','facts','rules','selected','retained','remaining'):
                    assert current[key]==stage[key],(arm,name,key)
                proof=save_result(current,out/'raw');receipts.append(current['receipt'])
                native_stages[name]=current
                fresh[name]=dict(source=source,native=proof,classification=current['classification'],
                    answer=current['answer'],contrary=current['contrary'],exact_channels_and_trace=True)
            diagnosis=witness(dict(stages={'Attack':native_stages['Attack']},query_domain_valid=True),out)
            expected=0 if arm in ('D-AB','D-BA') else 11 if arm=='historical-shared' else 1 if arm=='overlap-1' else 6 if arm=='overlap-6' else 12
            assert len(diagnosis['diagnostic']['overlap'])==expected
            rows[arm]=dict(stages=fresh,diagnostic=diagnosis,
                observed_parent_refs=None,parent_observability='Returned selections/retained beliefs and native guard diagnostic; fired-rule parents not exposed')
        recursive=minimal(out/'recursive');dependence=dependencies(out/'dependencies')
        assert recursive['symbolic']['classification']=='unknown'
        assert recursive['diagnostic']['overlap']==['rule_extend-empty']
        assert dependence['diamond']['classification']=='unknown'
        assert dependence['diamond-disjoint-inputs']['classification']=='supported-positive'
        assert dependence['single-delivery']['answer']==dependence['replayed-input']['answer']
        assert dependence['circular-chain']['answer']['stamps']==['obs_audit_origin']
    return record(out/'summary.json',dict(schema='cycle18-native-replay-v1',passed=True,arms=rows,
        recursive=recursive,dependencies=dependence,oracle_disabled=True,
        scope='Exact original inputs and answer/selection/retention parity; reference outputs never passed to native execution'))
