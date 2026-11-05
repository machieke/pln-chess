"""Complete regression, abstention, induction and isolated performance evidence."""
from collections import Counter
import copy,resource,subprocess,sys
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.api import explain_move
from pln_chess.learning import Model
from pln_chess.cycle4.inference import infer_moves
from pln_chess.cycle3.native import NativeSession
from evaluation.cycle3 import read_gzip
from scripts.cycle4_baseline import pack


def research(dataset,models,runtime,out):
    from evaluation.cycle4_induction import experiment
    experiment(dataset,models['C4-full'],runtime,out/'ablations/induction.json')
    cases=[];counts=Counter();comparisons=[];regressions=[]
    for prefix,split in [('frozen','heldout-transfer'),('frozen','adversarial'),('cycle3','independent-games'),
                         ('cycle4','structural-combination'),('cycle4','independent-games')]:
        before=read_gzip(out/f'evaluation/C3-{prefix}-{split}.json.xz')
        after=read_gzip(out/f'evaluation/C4-full-{prefix}-{split}.json.xz')
        by={(r['fixture'],r['move']):r for r in after['rows']}
        for r in before['cases']:
            counts[r['root_cause']]+=1
            cases.append({**r,'evaluation_artifact':f'evaluation/C3-{prefix}-{split}.json.xz',
                          'c4':by[(r['fixture'],r['move'])]})
        for r in before['rows']:
            a=by[(r['fixture'],r['move'])]
            comparisons.append({'dataset':prefix,'split':split,'fixture':r['fixture'],'move':r['move'],'label':r['label'],
                                'root_cause':r['root_cause'],'before':r['classification'],'after':a['classification'],
                                'before_tv':r['truth_value'],'after_tv':a['truth_value'],'proof_before':r['proof_id'],'proof_after':a['proof_id']})
            if a['classification']=='supported' and not a['label']:
                regressions.append({'case':a,'explanation':'Conditional local support was not defeated by a sufficiently strong learned constraint. Inspect all matched and losing proof paths in the referenced evaluation artifact.',
                                    'artifact':f'evaluation/C4-full-{prefix}-{split}.json.xz'})
    pack(out/'proofs/error-case-ledger.json.xz',cases);pack(out/'proofs/all-classification-transitions.json.xz',comparisons)
    write_json(out/'error-taxonomy.json',{'cases':len(cases),'ranked':dict(counts.most_common()),
        'case_ledger':'proofs/error-case-ledger.json.xz','all_transitions':'proofs/all-classification-transitions.json.xz',
        'definition':'Every C3 unknown, incomplete, false legal or false negative across the declared regressions and new holdouts. No candidate selection before counting.',
        'ranking':'Descending frequency, ties in stable dataset order; generality reviewed in coverage.md.'})
    write_json(out/'regressions.json',regressions)
    # All 23 + 26 original Cycle 2 false legal cases, including cases already fixed in C3.
    b1=Model.load(ROOT/'artifacts/cycle2/B1-model.json',runtime);old_errors=[]
    for split in ('heldout-transfer','adversarial'):
        report=read_json(ROOT/f'artifacts/cycle2/B1-{split}.json')
        frozen=read_json(ROOT/'artifacts/cycle2/dataset.json');fixtures={p['id']:p for p in frozen['positions']}
        for r in report['rows']:
            if r['label'] or r['classification']!='supported':continue
            fen=fixtures[r['fixture']]['fen'];proofs={}
            for name,model in [('C2',b1),('C3',models['C3']),('C4',models['C4-full'])]:
                proofs[name]=explain_move(fen,r['move'],model,runtime=runtime)
            old_errors.append({'split':split,'fixture':r['fixture'],'fen':fen,'move':r['move'],'proofs':proofs,
                               'transition':[proofs[n]['candidate']['classification'] for n in ('C2','C3','C4')]})
    assert len(old_errors)==49
    pack(out/'proofs/original-49-errors.json.xz',old_errors)
    write_json(out/'original-errors-summary.json',{'count':len(old_errors),'transitions':dict(Counter(' -> '.join(r['transition']) for r in old_errors)),
        'by_split':{s:dict(Counter(' -> '.join(r['transition']) for r in old_errors if r['split']==s)) for s in ('heldout-transfer','adversarial')},
        'artifact':'proofs/original-49-errors.json.xz'})
    selected=[];seen=set()
    for c in cases:
        if c['root_cause'] in seen:continue
        a=c['c4']
        if c['classification']=='unknown' and a['classification']==('supported' if c['label'] else 'contradicted'):
            selected.append(c);seen.add(c['root_cause'])
        if len(selected)>=6:break
    failure=next((c for c in cases if c['label'] and c['c4']['classification']!='supported'),None)
    if failure:selected.append(failure)
    proof_examples=[]
    for c in selected:
        before=explain_move(c['fen'],c['move'],models['C3'],runtime=runtime)
        after=explain_move(c['fen'],c['move'],models['C4-full'],runtime=runtime)
        proof_examples.append({'fixture':c['fixture'],'fen':c['fen'],'move':c['move'],'family':c['root_cause'],'label':c['label'],
                               'resolved':after['candidate']['classification']==('supported' if c['label'] else 'contradicted'),
                               'before':before,'after':after})
    pack(out/'proofs/before-after-examples.json.xz',proof_examples)
    write_json(out/'proof-examples-summary.json',[{'fixture':c['fixture'],'move':c['move'],'family':c['family'],'resolved':c['resolved'],
        'before_class':c['before']['candidate']['classification'],'after_class':c['after']['candidate']['classification'],
        'before_tv':c['before']['candidate']['legal_move_truth_value'],'after_tv':c['after']['candidate']['legal_move_truth_value'],
        'rules':c['after']['candidate']['matched_rule_ids']} for c in proof_examples])
    # Reference/cold/warm equality of every candidate including complete native proofs.
    frozen=read_json(ROOT/'artifacts/cycle2/dataset.json');benchmark_positions=[next(p for p in frozen['positions'] if p['id']=='game-0')]
    benchmark_positions += [next(p for p in dataset['positions'] if p['split']==s) for s in ('structural-combination','independent-games')]
    write_json(out/'benchmarks/positions.json',benchmark_positions)
    for name,checkpoint in [('inference',out/'model/C4-full.json'),('C3-reference',ROOT/'artifacts/cycle3/C3-full-model.json')]:
        subprocess.run([sys.executable,'-m','evaluation.cycle4_benchmark','--checkpoint',str(checkpoint),
                        '--positions',str(out/'benchmarks/positions.json'),'--output',str(out/f'benchmarks/{name}.json')],check=True)
    write_json(out/'benchmarks/research-process.json',{'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'scope':'Entire parent research process including complete diagnostic and provenance reports; not inference-only.'})
    print('RESEARCH COMPLETE',flush=True)
