"""Controlled transfer, causal induction and premise-removal experiments."""
import copy,tempfile
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import TV,UNKNOWN
from pln_chess.domain import Position
from pln_chess.api import find_move,explain_move
from pln_chess.learning import PRIOR
from pln_chess.cycle4.model import FactoredModel
from pln_chess.cycle5.model import train
from pln_chess.cycle5.inference import infer_moves,counterfactual,Cycle5Options
from pln_chess.cycle5.ontology import descriptors
from pln_chess.cycle5.history import inspect
from pln_chess.inference import classify,Options
from evaluation.cycle3 import read_gzip
from scripts.cycle4_baseline import pack

def induction(dataset,runtime,model):
    # Learn a candidate consequent rule absent from the supplied model. The
    # bounded symbolic proposal is host search, not native concept invention.
    old=read_json(ROOT/'artifacts/cycle4/datasets/dataset.json');groups={}
    for r in old['examples']:groups.setdefault(r['dependence_group'],r)
    population=[];seen=set();excluded=[]
    for group,r in sorted(groups.items()):
        ancestry=set([group]+r.get('transformation_lineage',[]))
        if ancestry&seen:excluded.append(group);continue
        seen.update(ancestry)
        o=descriptors(Position.from_fen(r['fen']),find_move(Position.from_fen(r['fen']),r['move']))
        population.append({'group':group,'source':r['source'],'evidence_id':digest(r),'geometry':next(x['descriptor'] for x in o['typed_relations'] if x['family']=='geometry'),
                           'destination':o['context']['destination'],'outcome':r['movement_label']})
    proposals=sorted({digest(r['geometry']):r['geometry'] for r in population}.items())[:64]
    rules=[]
    for key,shape in proposals:
        a=[r for r in population if r['geometry']==shape];b=[r for r in a if r['destination']=='Empty']
        if not b or len(a)==len(population):continue
        n=len(population);counts={'N':n,'A':len(a),'B':len(b),'C':sum(r['outcome'] for r in population),'BA':len(b),'BC':sum(r['outcome'] for r in b)}
        conf=runtime.batch([('confidence',f'(stv 1.0 (Truth_w2c {float(len(b))}))')])['confidence'].confidence
        inputs=[TV(v,conf) for v in (len(a)/n,len(b)/n,counts['C']/n,1.,counts['BC']/len(b))]
        expr='(Truth_Induction '+' '.join(v.metta() for v in inputs)+')';tv=runtime.batch([('induced',expr)])['induced']
        rules.append({'id':'experimental-induction:'+key,'descriptor':shape,'counts':counts,'inputs':[x.json() for x in inputs],
                      'expression':expr,'truth_value':tv.json(),'evidence_ids':[r['evidence_id'] for r in population],
                      'dependence_groups':[r['group'] for r in population],'scope':'Geometry -> local pseudo-admissibility; destination/path/safety are not proven.'})
    tasks=[]
    for r in dataset['factorial_test']:
        p=Position.from_fen(r['fen']);o=descriptors(p,find_move(p,r['move']));shape=next(x['descriptor'] for x in o['typed_relations'] if x['family']=='geometry')
        h=next((x for x in rules if x['descriptor']==shape),None)
        expression=f'(Truth_ModusPonens (stv 1.0 0.99) {TV.from_json(h["truth_value"]).metta() if h else UNKNOWN.metta()})'
        expressions=[('disabled',f'(Truth_ModusPonens (stv 1.0 0.99) {UNKNOWN.metta()})'),('enabled',expression),('sham',expression)]
        values=runtime.batch(expressions);tv=values['enabled'];actual=explain_move(r['fen'],r['move'],model,runtime=runtime)['candidate']
        tasks.append({'source':r['source'],'fen':r['fen'],'move':r['move'],'oracle_legal':r['label'],
                      'native_arms':[{'arm':arm,'expression':expr,'output':values[arm].json()} for arm,expr in expressions],
                      'disabled':{'local_tv':values['disabled'].json(),'global_class':actual['classification']},
                      'enabled':{'rule':h['id'] if h else None,'local_tv':tv.json(),'local_class':classify(tv,Options()),'global_class':actual['classification']},
                      'sham_redundant':{'local_tv':values['sham'].json(),'global_class':actual['classification'],'reason':'Duplicate inferred rule with identical ancestry; native activation reexecuted, no extra revision.'},
                      'global_scope':'Actual strict planner result retained: experimental geometry-to-local rules are not global legality theorems; no production rule injection.',
                      'global_proof_plan':actual['proof_plan']})
    return {'population':population,'excluded_ancestor_groups':excluded,'sampling':'First original training row per dependence group, excluding shared transform ancestry; no final-holdout labels in marginals or proposals.',
            'rules':rules,'tasks':tasks,'proposal_budget':64,'native_rule_discovery':False,
            'global_classification_changes':0,'local_activations':sum(x['enabled']['local_class']=='supported' for x in tasks),
            'local_false_legal_if_misused':sum(x['enabled']['local_class']=='supported' and not x['oracle_legal'] for x in tasks),
            'conclusion':'Consequent conditionals are newly induced, but host-suggested geometry descriptors are not new native abstractions. Local activation cannot establish missing destination/path/safety composition. No production induction benefit; default remains disabled.'}

def factorial(dataset,full,runtime,out,induced):
    bridge=full.base_model();bridge.hypotheses={k:h for k,h in bridge.hypotheses.items() if h['target']=='Bridge'}
    with tempfile.TemporaryDirectory(prefix='pln-c5-factorial-') as tmp:
        model=train(dataset['factorial_evidence'],bridge,runtime,Path(tmp)/'ledger.jsonl')
    model.export(out/'model/C5-factorial-only.json')
    # Deliberately absolute comparator. Its exact square context is explicitly
    # confined to this diagnostic baseline, never used by production inference.
    absolute={}
    for r in dataset['factorial_train']:
        p=Position.from_fen(r['fen']);m=find_move(p,r['move']);key=(p.at(m.start).kind,m.start,m.end,descriptors(p,m)['context']['destination'])
        if key not in absolute:
            absolute[key]=runtime.batch([('revision',f'(Truth_Revision {PRIOR.metta()} {TV(float(r["label"]),.5).metta()})')])['revision']
    tasks=[]
    for r in dataset['factorial_test']:
        p=Position.from_fen(r['fen']);m=find_move(p,r['move']);results={}
        for name,variant in [('C5-factored','C5-full'),('C5-abstract-only','C5-abstract-only'),('C5-no-new-negatives','C5-no-new-negatives')]:
            model.variant=variant;results[name]=infer_moves(p,model,runtime=runtime,selected_moves=[m])['candidates'][0]
        results['C4-frozen']=explain_move(p,m,full.base_model(),runtime=runtime)['candidate']
        key=(p.at(m.start).kind,m.start,m.end,descriptors(p,m)['context']['destination']);tv=absolute.get(key,UNKNOWN)
        tasks.append({'id':r['source'],'fen':r['fen'],'move':r['move'],'label':r['label'],'family':r['structural_family'],
                      'results':results,'absolute_baseline':{'truth_value':tv.json(),'classification':classify(tv,Options()),'key':repr(key)},
                      'induction':next(x for x in induced['tasks'] if x['source']==r['source'])})
    # Measure prefixes of distinct supervised contexts, with grouping preserved.
    unique=[];seen=set()
    for r in dataset['factorial_evidence']:
        key=(r['abstract_combination'],tuple(x['family'] for x in r['targets']))
        if key not in seen:seen.add(key);unique.append(r)
    efficiency={t['id']:{'first_correct_global_contexts':None,'first_matching_geometry_contexts':None} for t in tasks}
    for n in sorted({1,len(unique)//2,len(unique)}):
        with tempfile.TemporaryDirectory(prefix='pln-c5-efficiency-') as tmp:prefix=train(unique[:n],bridge,runtime,Path(tmp)/'e.jsonl')
        for t in tasks:
            c=explain_move(t['fen'],t['move'],prefix,runtime=runtime)['candidate'];e=efficiency[t['id']]
            if e['first_correct_global_contexts'] is None and c['classification']==('supported' if t['label'] else 'contradicted'):e['first_correct_global_contexts']=n
            if e['first_matching_geometry_contexts'] is None and any(p['family']=='geometry' and p['truth_value']['confidence']>.25 for p in c['typed_premises']):e['first_matching_geometry_contexts']=n
    return {'tasks':tasks,'sample_efficiency':efficiency,'measured_prefixes':sorted({1,len(unique)//2,len(unique)}),'distinct_training_contexts':len(unique),
            'efficiency_scope':'First success among measured prefix checkpoints, not an exhaustive minimal sample count.',
            'leakage_audit':dataset['leakage_audit'],'prior':'Only frozen independent C4 bridge conditionals are supplied to the factorial model; no C4 observation/context hypotheses.'}

def research(dataset,model,runtime,out):
    induced=induction(dataset,runtime,model);write_json(out/'induction.json',induced)
    pack(out/'factorial.json.xz',factorial(dataset,model,runtime,out,induced))
    prior=read_gzip(ROOT/'artifacts/cycle4/proofs/original-49-errors.json.xz');regressions=[]
    for row in prior:
        c=explain_move(row['fen'],row['move'],model,runtime=runtime)['candidate']
        regressions.append({**row,'C5':c,'transition':row['transition']+[c['classification']]})
    pack(out/'proofs/original-49-errors.json.xz',regressions)
    assert all(r['C5']['classification']=='contradicted' for r in regressions)
    examples=[]
    for f in dataset['positions']:
        if f['split'] in ('combination-holdout','structural-holdout'):
            examples.append({'fixture':f['id'],'fen':f['fen'],'move':f['focus_move'],
                'C4':explain_move(f['fen'],f['focus_move'],model.base_model(),runtime=runtime)['candidate'],
                'C5':explain_move(f['fen'],f['focus_move'],model,runtime=runtime)['candidate']})
    pack(out/'proofs/before-after.json.xz',examples)
    tests=[('k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1','e3f3'),('2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1','f6h5'),
           ('7k/8/8/8/8/8/2RP4/2K5 w - - 0 1','c2h2')]
    pack(out/'proofs/family-counterfactuals.json.xz',[counterfactual(f,m,model,runtime=runtime) for f,m in tests])
    before='7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1';p=Position.from_fen(before);after=p.successor(find_move(p,'b7b5')).fen()
    evidence={'source':'independent-event-observation','confidence':.9,'initial_fen':before,'moves':['b7b5']}
    write_json(out/'temporal.json',{'modes':{m:inspect(after,m,None if m=='fen-only' else evidence) for m in ('fen-only','trusted-metadata','event-backed')},
        'conflict':inspect(before,'event-backed',evidence),'truncated':inspect(before,'event-backed',{**evidence,'moves':[]})})
    # Every newly supported negative receives a native proof and a causal
    # evidence-family removal. Alternative surviving witnesses remain visible.
    from dataclasses import replace
    comparison=read_json(out/'comparison.json');new=[]
    for split in comparison['C5-full']:
        old=read_gzip(out/comparison['C4'][split]['artifact']);current=read_gzip(out/comparison['C5-full'][split]['artifact'])
        index={(r['fixture'],r['move']):r for r in old['rows']}
        for row in current['rows']:
            before_row=index[row['fixture'],row['move']]
            if before_row['classification']!='unknown' or row['classification']!='contradicted':continue
            c=explain_move(row['fen'],row['move'],model,runtime=runtime)['candidate'];nodes={t['id']:t for t in c['proof_trace']}
            todo=[c['selected_negative_witness']];families=set();visited=set()
            while todo:
                node=todo.pop()
                if node in visited:continue
                visited.add(node);t=nodes[node]
                families.update(model.hypotheses[k]['family'] for k in t['matched_rule_ids'] if k in model.hypotheses)
                todo.extend(p['node'] for p in t['premises'] if 'node' in p)
            suppressed=explain_move(row['fen'],row['move'],model,Cycle5Options(suppress_families=tuple(sorted(families))),runtime)['candidate']
            new.append({'split':split,'row':row,'before':before_row,'native_proof':c,'removed_families':sorted(families),'without_decisive_family':suppressed})
    pack(out/'proofs/new-negative-counterfactuals.json.xz',new)
    write_json(out/'new-negative-summary.json',{'count':len(new),'by_split':{s:sum(x['split']==s for x in new) for s in comparison['C5-full']},
        'by_piece':{p:sum(x['row']['piece']==p for x in new) for p in sorted({x['row']['piece'] for x in new})},
        'removal_changes_classification':sum(x['without_decisive_family']['classification']!='contradicted' for x in new),
        'false_illegal':sum(x['row']['label'] for x in new)})
