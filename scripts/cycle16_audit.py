"""Post-run provenance audits; no production answer is reconstructed here."""
import argparse
import json
import re
from pathlib import Path
from pln_chess.common import ROOT,read_json,digest
from research.cycle15.native_reasoner import alpha_key,parse
from research.cycle16.evidence_audit import pair_diagnostic
from research.cycle16.records import record


def shared_witness(out):
    out=Path(out)
    source=read_json(out/'budgets/budgets-learning.json')['shared-chain-witness']
    native=read_json(source['result']['stages']['Attack']['proof']['path'])
    clear=source['clearance'];node=parse(clear['term'])
    _,attacker,target,shape,state=node
    expected=f'(Implication (Clear {attacker} $target {shape} {state}) (Attack {attacker} $target {state}))'
    partial=next(r for r in native['retained'] if alpha_key(r['term'])==alpha_key(expected))
    diagnostic=pair_diagnostic(partial,clear,out/'supplement')
    assert diagnostic['overlap'] and all(s.startswith('train_') for s in diagnostic['overlap'])
    assert diagnostic['markers'][0][1]=='false' and diagnostic['markers'][2][1]
    return record(out/'supplement/shared-training-witness.json',dict(passed=True,diagnostic=diagnostic,
        source=source['result']['stages']['Attack']['proof'],
        explanation='The terminal partial retains an unbound target. The earlier exact-ground lookup returned null; '
            'this audit selects the actually returned schema modulo variable renaming and lets the native operator bind it.',
        scope='Structural possibility plus verified guard rejection; no fabricated scheduler event or production answer'))


def proof_audit(out):
    out=Path(out);counts=dict(records=0,selected=0,retained=0,remaining=0,answer_channels=0);failures=[];programs={}
    exclude={'preservation','packs','restored-evidence','reproduction-source'}
    for path in sorted(out.rglob('*.json')):
        if any(part in exclude for part in path.relative_to(out).parts):continue
        if path.parent.name!='raw':continue
        d=read_json(path)
        values=d.get('stages',{}).values() if 'stages' in d else [d]
        for result in values:
            if not all(k in result for k in ('facts','rules','receipt','selected','retained')):continue
            key=digest(result)
            if key in programs:continue
            programs[key]=result['receipt']['program_sha256'];counts['records']+=1
            allowed={s for f in result['facts']+result['rules'] for s in f['stamps']}
            for group in ('selected','retained','remaining'):
                for sentence in result[group]:
                    counts[group]+=1
                    if not sentence['stamps'] or not set(sentence['stamps'])<=allowed:
                        failures.append(dict(path=str(path),group=group,sentence=sentence))
            for name in ('answer','contrary'):
                if result[name]:
                    counts['answer_channels']+=1
                    if not set(result[name]['stamps'])<=allowed:failures.append(dict(path=str(path),group=name))
    assert not failures,failures
    return record(out/'supplement/proof-audit.json',dict(passed=True,counts=counts,failures=failures,
        scope='Every retained native derivation record at audit time; all output stamps originate in its actual input',
        fired_rule_tree_available=False))


def bounded_controls(out):
    from research.cycle15.native_reasoner import NativeReasoner,Budgets
    from research.cycle16.experiments import fixture,observations,knowledge,GENEROUS
    from research.cycle16.records import compact
    out=Path(out);reasoner=NativeReasoner();state,a,t=fixture(tag='bounded_audit')
    facts,_=observations(state,a,t);rules=knowledge('F');query=f'(Attack {a} {t} {state["id"]})'
    rows={}
    for name,budget,mode in [('query-api',GENEROUS,'query'),
                            ('retention-pressure',Budgets(64,8,8,15),'derive'),
                            ('actual-timeout',Budgets(64,128,256,.001),'derive')]:
        result=reasoner.infer(facts,rules,query,budgets=budget,mode=mode)
        rows[name]=compact(result,out/'supplement')
        if name=='retention-pressure':
            supplied={alpha_key(s.term) for s in facts+rules}
            retained={alpha_key(s['term']) for s in result['retained']}
            rows[name]['initial_statements_not_retained']=sorted(supplied-retained)
            rows[name]['scope']='Observed retention loss, not an invented per-item eviction trace'
    assert rows['query-api']['classification']=='supported-positive'
    assert rows['actual-timeout']['classification']=='incomplete'
    assert rows['retention-pressure']['initial_statements_not_retained']
    return record(out/'supplement/bounded-controls.json',rows)


def role_state_controls(out):
    import copy
    from dataclasses import replace
    from research.cycle15.native_reasoner import NativeReasoner
    from research.cycle15.observations import successor
    from research.cycle16.experiments import fixture,observations,knowledge,GENEROUS,infer
    from research.cycle16.records import compact
    out=Path(out);reasoner=NativeReasoner();state,a,t=fixture('OE',tag='same_entity_states')
    blocker=next(p for p in state['pieces'] if p['id'].startswith('blocker'))
    after=successor(state,dict(id='move_same_entities',piece=blocker['id'],destination=[0,0]))
    before_facts,_=observations(state,a,t);after_facts,_=observations(after,a,t)
    query=f'(Attack {a} {t} {after["id"]})';rules=knowledge('F')
    # The second ray cell is already empty before the move, but its old-state
    # observation must not replace the omitted same-cell after-state observation.
    before_empty={f.term.split()[1] for f in before_facts if f.term.startswith('(Empty ')}
    removed=next(f for f in after_facts if f.term.startswith('(Empty ') and f.term.split()[1] in before_empty)
    rows={}
    for name,fs in [('mixed-correct-states',after_facts+before_facts),
                    ('stale-empty-cannot-fill-after-gap',[f for f in after_facts if f!=removed]+before_facts)]:
        rows[name]=compact(reasoner.infer(fs,rules,query,budgets=GENEROUS),out/'supplement')
    assert rows['mixed-correct-states']['classification']=='supported-positive'
    assert rows['stale-empty-cannot-fill-after-gap']['classification']=='unknown'
    clear,a,t=fixture(tag='role_supplement');facts,_=observations(clear,a,t)
    wrong=[replace(f,term=f.term.replace(t,'unrelated_target')) if f.term.startswith('(RayPath ') else f for f in facts]
    rows['wrong-ray-target']=compact(reasoner.infer(wrong,rules,f'(Attack {a} {t} {clear["id"]})',budgets=GENEROUS),out/'supplement')
    friendly=copy.deepcopy(clear);friendly['id']+='friendly_attacker';friendly['pieces'][0]['owner']='white'
    result=infer(friendly,a,t,budgets=GENEROUS)
    rows['friendly-attacker']=compact(result,out/'supplement')
    assert result['stages']['Attack']['classification']=='supported-positive'
    assert result['stages']['Exposure']['classification']=='unknown'
    assert rows['wrong-ray-target']['classification']=='unknown'
    return record(out/'supplement/role-state-controls.json',rows)


def threshold_control(out):
    from dataclasses import replace
    from research.cycle15.native_reasoner import NativeReasoner
    from research.cycle16.experiments import fixture,observations,knowledge,GENEROUS,support_status
    from research.cycle16.records import compact
    out=Path(out);state,a,t=fixture(tag='below_threshold');facts,_=observations(state,a,t)
    rules=[replace(r,confidence=.05) if r.stamps[0]=='rule_clear-two' else r for r in knowledge('F')]
    result=NativeReasoner().infer(facts,rules,f'(Attack {a} {t} {state["id"]})',budgets=GENEROUS)
    assert result['classification']=='unknown' and result['answer'] is not None
    assert result['answer']['confidence']<.1 and not result['incomplete']
    return record(out/'supplement/below-threshold.json',dict(result=compact(result,out/'supplement'),
        support_status=support_status(result),display_thresholds_unchanged=True,
        scope='Low-confidence supplied-rule diagnostic, not a change to any primary arm'))


def transfer_audit(out):
    from collections import Counter
    from research.cycle16.corpus import roots,groups
    items=roots();prior=[r for r in items if r['split']!='test'];test=[r for r in items if r['split']=='test']
    def location(row):
        pieces={p['id']:p for p in row['state']['pieces']}
        return tuple(pieces[row['attacker']]['cell']),tuple(pieces[row['target']]['cell'])
    seen={location(r) for r in prior};entities={r[k] for r in prior for k in ('attacker','target')}
    result=dict(registered_before_learning=True,groups=groups(items),test_source_episodes=len(test),
        source_ancestry_overlap=sorted({r['source_ancestry'] for r in test}&{r['source_ancestry'] for r in prior}),
        test_query_bindings=2*len(test),unseen_test_query_identifiers=sum(r[k] not in entities for r in test for k in ('attacker','target')),
        test_roots_with_unseen_endpoint_locations=sum(location(r) not in seen for r in test),
        endpoint_location_pairs={s:[dict(attacker=list(a),target=list(t),roots=count) for (a,t),count in
            Counter(location(r) for r in items if r['split']==s).items()] for s in ('train','development','test')},
        attacker_kinds={s:dict(Counter(next(p['kind'] for p in r['state']['pieces'] if p['id']==r['attacker'])
            for r in items if r['split']==s)) for s in ('train','development','test')},
        test_target_kinds=dict(Counter(next(p['kind'] for p in r['state']['pieces'] if p['id']==r['target']) for r in test)),
        claim='Unseen source episodes and identifiers; no unseen endpoint-location or coarse-geometry transfer. Transformations are dependent controls.',
        independence='Common opening configurations and engine tournament source; no independent-population confidence interval')
    return record(Path(out)/'supplement/transfer-audit.json',result)


def resources(out):
    out=Path(out);seen=set();records=[];sizes={}
    for path in out.rglob('*'):
        if not path.is_file() or any(part in ('packs','restored-evidence','reproduction-source') for part in path.relative_to(out).parts):continue
        group=path.relative_to(out).parts[0];sizes[group]=sizes.get(group,0)+path.stat().st_size
        if path.suffix!='.json' or path.parent.name!='raw':continue
        d=read_json(path)
        candidates=[d]
        if 'stages' in d:candidates.extend(d['stages'].values())
        for value in candidates:
            receipt=value.get('receipt',value)
            if 'native_processes' not in receipt or 'program' not in receipt:continue
            key=digest(receipt)
            if key in seen:continue
            seen.add(key);records.append(receipt)
    timed_jobs=[]
    for path in sorted((out/'preservation/commands').glob('*.json')):
        command=read_json(path);log=Path(command['log']).read_text(errors='replace')
        cpu=re.findall(r'(?:User|System) time \(seconds\): ([\d.]+)',log)
        memory=re.search(r'Maximum resident set size \(kbytes\): (\d+)',log)
        timed_jobs.append(dict(command=path.name,cpu_seconds=sum(map(float,cpu)) if len(cpu)==2 else None,
            peak_rss_kib=int(memory[1]) if memory else None))
    result=dict(unique_retained_native_processes=len(records),
        cpu_seconds=sum(r.get('cpu_seconds') or 0 for r in records),
        peak_rss_kib=max((r.get('peak_rss_kib') or 0 for r in records),default=0),
        incomplete_native_receipts=sum(r.get('incomplete',False) for r in records),
        generated_bytes_by_group=sizes,
        research_bytes=sum(v for k,v in sizes.items() if k!='preservation'),
        preservation_bytes=sizes.get('preservation',0),
        preservation_timed_jobs=len(timed_jobs),
        preservation_measured_cpu_seconds=sum(r['cpu_seconds'] or 0 for r in timed_jobs),
        preservation_max_job_rss_kib=max((r['peak_rss_kib'] or 0 for r in timed_jobs),default=0),
        preservation_timing_records=timed_jobs,
        accounting_scope='Deduplicated retained research receipts and GNU-time completed preservation jobs; '
            'exploratory commands, interrupted partial work, and the final parallel proof-comparison CPU are not fully metered')
    assert result['unique_retained_native_processes']<10000 and result['cpu_seconds']<8*3600
    assert result['research_bytes']<2*1024**3 and result['preservation_bytes']<8*1024**3
    assert result['preservation_measured_cpu_seconds']<24*3600
    return record(out/'resource-census.json',result)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('shared_witness','proof_audit','resources','bounded_controls','role_state_controls','threshold_control','transfer_audit'));p.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(globals()[a.command](a.out),indent=2))
