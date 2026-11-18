"""Actual refits, strict stale rejection and independently rebuilt active views."""
import copy
from pathlib import Path
import time
from pln_chess.common import digest
from .lifecycle import Journal,Cache,StaleEvidence
from .measurements import measure,matrix
from .learning import fit
from .native import request
from .records import record


def rejects(fn,kind=ValueError):
    try:fn()
    except kind:return True
    raise AssertionError('Expected rejection did not occur')


def proof(result):return {k:v['observable_sha256'] for k,v in result['stages'].items()}


def run(journal,episodes,annotations,models,roots,out,*,compact=False):
    out=Path(out);j=Journal.historical(journal.snapshot());checks={};timings={}
    first=next(e for e in episodes if e['split']=='A' and e['variant']=='natural')
    root=next(r for r in roots if r['id']==first['root']);env=first['environment'];model=models['D-AB']
    cache=Cache()
    def clocked(name,fn):
        start=time.perf_counter();value=fn();timings[name]=time.perf_counter()-start;return value
    cold,_=clocked('cold_query',lambda:request(j,env,model['generation'],arm='D-AB',out=out/'raw',cache=cache))
    warm,hit=clocked('warm_cache_lookup',lambda:request(j,env,model['generation'],arm='D-AB',out=out/'raw',cache=cache))
    assert cold==warm and hit['native_calls']==0;checks['cache_exact_proof_parity']=True
    checks['same_event_idempotent']=j.add('environment',j.node(env)['payload'])==env
    alias=j.add('environment',j.node(env)['payload'],ident='duplicate_delivery_'+env)
    alias_measure=measure(j,alias)
    # Same payload under another event ID is retained, but cannot become an
    # extra independent training source. Canonical delivery is reused below.
    checks['identical_payload_new_id_retained']=alias!=env
    checks['changed_payload_same_id_rejected']=rejects(lambda:j.add('environment',{'changed':True},ident=env))
    # A disconnected branch with the same statistical ancestry has no edge.
    disconnected=j.add('unrelated',dict(ancestry=root['source_ancestry'],note='No environmental dependency'))
    if not compact:
        duplicate=fit(j,annotations+annotations,out/'duplicate','D-AB')
        reverse=fit(j,list(reversed(annotations)),out/'reverse','D-AB')
        assert duplicate['model']==model['model'] and reverse['model']==model['model']
        checks['duplicate_and_reverse_model_identity']=True
        # A different ID for the same observation is not admitted as extra
        # support; conflicting lineage is rejected before a second revision.
        checks['alias_annotation_not_independent']=rejects(lambda:fit(j,
            [first['measurement']['annotations']['Clear'],alias_measure['annotations']['Clear']],out/'alias-rejection','D-AB'))
        removed=fit(j,annotations,out/'remove-all-clear','D-AB',remove_support=('clear-two',))
        removed_result,_=request(j,env,removed['generation'],arm='remove-all-clear',out=out/'raw')
        record(out/'removed-support.json',removed_result)
        checks['removed_all_support_native_unknown']=removed_result['stages']['Attack']['classification']=='unknown'
    leave=clocked('leave_one_source_actual_refit',lambda:fit(j,annotations,out/'leave-one','D-AB',exclude=(root['source_ancestry'],)))
    leave_result,_=request(j,env,leave['generation'],arm='leave-one',out=out/'raw')
    assert root['source_ancestry'] not in leave['model']['rules']['clear-two']['ancestry']
    record(out/'leave-one-result.json',leave_result);checks['leave_one_actual_refit']=True
    if not compact:
        binding={}
        for name,kwargs in [('rule-removal',dict(remove=('clear-two',))),('premise-removal',dict(drop_empty=True)),
            ('wrong-state',dict(query_state='wrong_state')),('wrong-role',dict(query_attacker='absent_attacker'))]:
            binding[name],_=request(j,env,model['generation'],arm=name,out=out/'raw',**kwargs)
            assert binding[name]['stages']['Attack']['classification']=='unknown'
        record(out/'binding-controls.json',binding);checks['binding_and_removal_controls']=True
    # Use a snapshot containing only the primary current model for the
    # correction transaction. Additional experiment models are separate views.
    base=Journal.historical(journal.snapshot())
    for name,item in models.items():
        if name!='D-AB':
            bad=base.descendants(item['generation']);base._active.difference_update(bad);base._stale.update(bad)
    base_cache=Cache();before,_=request(base,env,model['generation'],arm='D-AB',out=out/'raw',cache=base_cache)
    # Retain a second application that depends on this generation and another
    # environment: both descendants must be invalidated by training correction.
    second=next(e for e in episodes if e['split']=='B' and e['variant']=='natural')
    second_result,_=request(base,second['environment'],model['generation'],arm='D-AB',out=out/'raw')
    disconnected=base.add('unrelated',dict(ancestry=root['source_ancestry'],note='Same game metadata; no edge'))
    snapshot=base.snapshot();record(out/'historical-snapshot.json',snapshot)
    affected=base.descendants(env);assert affected==base.full_descendants(env)
    assert before['application'] in affected and second_result['application'] in affected and disconnected not in affected
    checks['branched_descendants_and_disconnected_branch']=True
    corrected=matrix(root,'OE')
    def rebuild(full,name):
        owner=Journal.historical(snapshot);tx=owner.supersede(env,'environment',corrected,full=full)
        assert rejects(lambda:owner.require(env),StaleEvidence)
        assert rejects(lambda:owner.require(model['generation']),StaleEvidence)
        assert rejects(lambda:owner.add('annotation',{},[env]),StaleEvidence)
        assert rejects(lambda:base_cache.get(before['cache_identity'],owner),StaleEvidence)
        assert rejects(lambda:fit(owner,annotations,out/(name+'-stale-fit'),'D-AB'),StaleEvidence)
        assert rejects(lambda:request(owner,env,model['generation'],out=out/'raw'),StaleEvidence)
        measured=measure(tx.draft,tx.new)
        current=[i for i in annotations if i not in tx.affected]+list(measured['annotations'].values())
        fresh=fit(tx.draft,current,out/(name+'-refit'),'D-AB')
        result,_=request(tx.draft,tx.new,fresh['generation'],arm='D-AB',out=out/'raw')
        view=tx.commit([tx.new,*measured['annotations'].values(),fresh['generation'],result['application']])
        assert owner.require(disconnected)
        assert measured['Clear']['value'] is False and measured['Attack']['value'] is False
        assert result['stages']['Attack']['classification']=='supported-negative'
        return dict(snapshot=view,environment=tx.new,measurement=measured,model=fresh,native=result,affected=sorted(tx.affected))
    incremental=clocked('incremental_correction_measure_refit_query',lambda:rebuild(False,'incremental'))
    full=clocked('full_reconstruction_measure_refit_query',lambda:rebuild(True,'full'))
    assert incremental['model']==full['model'] and proof(incremental['native'])==proof(full['native'])
    assert incremental['snapshot']==full['snapshot']
    record(out/'incremental.json',incremental);record(out/'full.json',full)
    checks.update(actual_training_correction_refit=True,incremental_full_exact_view_and_proof_parity=True,
        stale_fit_query_annotation_cache_rejected=True,explicit_supersession=True)
    # Failure leaves published history intact and current access blocked.
    failed=Journal.historical(snapshot);transaction=failed.supersede(env,'environment',corrected)
    try:raise RuntimeError('Injected interruption before measurement/refit/publication')
    except RuntimeError:pass
    assert failed.pending and rejects(lambda:failed.snapshot(),StaleEvidence)
    assert rejects(lambda:transaction.commit([transaction.new]))
    checks['failed_rebuild_fail_closed']=True
    replay=Journal.historical(snapshot);historical,_=request(replay,env,model['generation'],arm='D-AB',out=out/'raw')
    assert proof(historical)==proof(before);checks['explicit_historical_native_replay']=True
    unknown=Journal.historical(snapshot);tx=unknown.supersede(env,'environment',matrix(root,'UE'))
    unknown_measure=measure(tx.draft,tx.new)
    unknown_result,_=request(tx.draft,tx.new,arm='F',out=out/'raw')
    assert unknown_measure['raw_antecedent'] is None and unknown_result['stages']['Attack']['classification']=='unknown'
    checks['unknown_correction_stays_unknown']=True
    identity=copy.deepcopy(journal.node(env)['payload'])
    for layer in ('reference','observed'):
        next(p for p in identity[layer]['pieces'] if p['id']==identity['attacker'])['id']='corrected_attacker'
        identity[layer]['id']='identity_correction_'+digest(identity[layer])[:24]
    # Keep the obsolete queried role to demonstrate unresolved/rejected binding.
    identity['observed']['id']=identity['reference']['id']
    changed=Journal.historical(snapshot);tx=changed.supersede(env,'environment',identity)
    identity_measure=measure(tx.draft,tx.new);identity_result,_=request(tx.draft,tx.new,out=out/'raw')
    assert identity_measure['unresolved'] and identity_result['stages']['Attack']['classification']=='unknown'
    checks['identity_correction_obsolete_binding_unknown']=True
    record(out/'unknown-correction.json',dict(measurement=unknown_measure,native=unknown_result))
    record(out/'identity-correction.json',dict(measurement=identity_measure,native=identity_result))
    assert all(checks.values())
    return record(out/'summary.json',dict(passed=True,checks=checks,timings_seconds=timings,
        before=before,cold=cold,warm=warm,leave_one=leave_result,correction=incremental['native'],
        performance_scope='Native cold/corrected queries and actual refits; warm is cache lookup, not native speed. Incremental/full timings include equal native work.',
        policy='Host-managed lifecycle; native stamps and calculus unchanged'))
