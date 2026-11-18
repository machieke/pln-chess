from copy import deepcopy
from dataclasses import replace
import os
from pathlib import Path
from unittest.mock import patch
import pytest

from pln_chess.common import ROOT,read_json
from research.cycle15.native_reasoner import NativeReasoner,Sentence,Budgets
from research.cycle20.compatibility import differences
from research.cycle20.controls import identity_controls
from research.cycle20.demonstrations import call
from research.cycle20.lifecycle import Generations
from research.cycle20.meter import metered
from research.cycle20.native import derive,projection,resume
from research.cycle20.observations import fixture,build
from research.cycle20.state import Identity,query_list,export,restore


@pytest.fixture(autouse=True)
def count_research_starts(tmp_path):
    with metered(Path(os.environ.get('C20_TEST_METER',tmp_path/'meter')),'cycle20-tests'):
        yield

def test_statewide_observation_event_identity():
    assert identity_controls()['passed']

@pytest.mark.parametrize('invalid',[[],['(State $s)'],['(State s extra)'],['(State (Unsupported s))']])
def test_queries_require_bounded_ground_data(invalid):
    with pytest.raises(ValueError):query_list(invalid)

def test_non_namespaced_stamp_fails_before_native_work():
    with patch.object(NativeReasoner,'execute_program',side_effect=AssertionError):
        with pytest.raises(ValueError,match='namespaced'):
            derive([Sentence('(State s)',stamps=('first',))],[],['(State s)'],Identity.create('s','e','f'))

def test_native_batch_matches_frozen_projection():
    example=read_json(ROOT/'artifacts/cycle19/demonstrations/positive.json')
    old=read_json(ROOT/example['native']['stages']['Attack']['native']['path'])
    qs=[old['query']]+([old['contrary_query']] if old['contrary_query'] else [])
    r=derive([Sentence(**s) for s in old['facts']],[Sentence(**s) for s in old['rules']],qs+qs,
             Identity.create('test','archived','archived','cycle19-local'),Budgets(**old['budgets']))
    assert not differences(projection(r,old['query'],old['contrary_query']),old)
    assert r['derivations']==1 and len(r['readouts'])==2*len(qs)

def test_partial_conditional_queue_round_trip_and_generation_rejection(tmp_path):
    s,roles=fixture();w=build(s,roles);first=call(w,12);key=first['state']['snapshot']
    path=tmp_path/'state.json';export(path,first['state'],w.identity)
    restored=restore(path,w.identity,key)
    assert '$' in str(restored['queues'])
    with pytest.raises(ValueError):restore(path,replace(w.identity,model='other'),key)
    child=resume(restored,w.identity,key,w.queries,6);whole=call(w,18)
    assert child['state']['queues']==whole['state']['queues']
    assert first['selected']+child['selected']==whole['selected']
    mutated=deepcopy(restored);mutated['queues'][1].reverse()
    with pytest.raises(ValueError):resume(mutated,w.identity,key,w.queries)

def test_capture_replacement_invalidates_consumers_and_inflight_read():
    s,roles=fixture();w=build(s,roles);manager=Generations()
    result=call(w,1)
    pending=manager.begin(['one','two'])
    old=manager.publish(pending,{'one':(w,result),'two':(w,result)})
    def invalidate_while_reading(*args):
        manager.invalidate_observation(w.lineage['source_events'][0])
        return result
    with patch.object(manager,'historic',side_effect=invalidate_while_reading):
        with pytest.raises(ValueError):manager.read(old['one'],w.queries)
    for ticket in old.values():
        with pytest.raises(ValueError):manager.check(ticket)
    with pytest.raises(ValueError):manager.publish(pending,{'one':(w,result),'two':(w,result)})
