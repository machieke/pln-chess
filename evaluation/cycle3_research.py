"""Executed error resolution, transfer, induction, learning curves and parity."""
import copy,hashlib,resource,tempfile
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position,Piece
from pln_chess.api import explain_move,find_move
from pln_chess.pln import TV
from pln_chess.cycle3.model import train
from pln_chess.cycle3.inference import infer_moves,Cycle3Options
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle3.descriptors import relation
from evaluation.cycle3 import read_gzip,write_gzip,evaluate

OUT=ROOT/'artifacts/cycle3'


def research(dataset,models,runtime):
    model=models['C3-full'];frozen=read_json(ROOT/'artifacts/cycle2/dataset.json')
    # Every original false positive, with outcome and complete native proof.
    baseline=read_gzip(OUT/'baseline-B1-heldout-transfer.json.gz');errors=[]
    for r in baseline['rows']:
        if not(r['self_check'] and not r['label'] and r['classification']=='supported'):continue
        result=explain_move(r['fen'],r['move'],model,runtime=runtime);c=result['candidate']
        resolved='correct-negative' if c['classification']=='contradicted' else 'abstention' if c['classification']=='unknown' else 'remaining-false-positive'
        errors.append({'fixture':r['fixture'],'fen':r['fen'],'move':r['move'],'baseline_tv':r['truth_value'],
                       'cause':'Missing bishop-diagonal or pawn-forward-diagonal attack hypothesis in frozen training.',
                       'outcome':resolved,'proof':result})
    write_gzip(OUT/'self-check-errors.json.gz',errors)
    write_json(OUT/'self-check-resolution.json',{'count':len(errors),'outcomes':{k:sum(e['outcome']==k for e in errors) for k in ('correct-negative','abstention','remaining-false-positive')},
               'cases':[{k:v for k,v in e.items() if k!='proof'}|{'classification':e['proof']['candidate']['classification'],'tv':e['proof']['candidate']['legal_move_truth_value']} for e in errors]})
    evidence={r['evidence_id']:r['payload'] for r in read_gzip(OUT/'C3-full-evidence.json.gz')}
    examples=[]
    # Reusable movement motifs at new distances, then attack and combined constraints.
    prior=read_json(ROOT/'artifacts/cycle2/demonstrations.json')
    specs=[(x['piece']+' relative motif',x['test_fixture']['fen'],x['test_fixture']['focus_move'],'local') for x in prior['generalization_examples']]
    specs.append(('Bishop king-exposure',errors[0]['fen'],errors[0]['move'],'attack'))
    pin=next(p for p in dataset['positions'] if p['id']=='challenge-diagonal-pin-Knight')
    specs.append(('Knight jump with newly combined exposure',pin['fen'],'e3f5','attack'))
    for name,fen,move,route in specs:
        result=explain_move(fen,move,model,runtime=runtime);c=result['candidate'];key=c['chosen_hypothesis_id']
        if route=='attack':
            chosen=next((a for a in c['attack_beliefs'] if a['truth_value']['strength']>=.8 and a['truth_value']['confidence']>=.25),None)
            key=chosen['id'] if chosen else key
        h=model.hypotheses.get(key,{})
        examples.append({'motif':name,'fen':fen,'move':move,'route':route,'hypothesis':h,'final_tv':c['legal_move_truth_value'],
                         'classification':c['classification'],'training':[{'evidence_id':eid,'input':evidence[eid]['input'],'source':evidence[eid]['source'],'group':evidence[eid]['dependence_group']} for eid in h.get('evidence_ids',[])],
                         'proof':result,'exact_context_used':any(r['tier']==6 for r in c['observations']['relations'])})
    # One obstruction motif at three independently placed late blockers.
    obstruction=[]
    for fen,move in [('7k/8/8/8/8/R1P5/1K6/8 w - - 0 1','a3d3'),
                     ('8/6k1/8/1R2P3/8/7n/2K5/8 w - - 0 1','b5g5'),
                     ('7k/8/8/8/R3P3/8/1K5n/8 w - - 0 1','a4g4')]:
        r=explain_move(fen,move,model,runtime=runtime);obstruction.append(r)
    write_gzip(OUT/'transfer-proofs.json.gz',{'examples':examples,'three_obstruction_transfers':obstruction})
    write_json(OUT/'transfer-summary.json',[{k:v for k,v in e.items() if k not in ('proof','hypothesis','training')}|
                 {'hypothesis_id':e['hypothesis'].get('id'),'descriptor':e['hypothesis'].get('descriptor'),
                  'conditional_tv':e['hypothesis'].get('positive'),'training':e['training'][:3]} for e in examples])
    # Re-execute all original induction formulas with their stored measured marginals.
    original=[]
    for key,h in models['B2'].induction.items():
        confidence=runtime.batch([('c',f'(stv 1.0 (Truth_w2c {float(h["counts"]["B"])}))')])['c'].confidence
        tvs=' '.join(TV(s,confidence).metta() for s in h['premises'])
        value=runtime.batch([('i','(Truth_Induction '+tvs+')')])['i'].json()
        original.append({'hypothesis':key,'counts':h['counts'],'premises':h['premises'],'stored_tv':h['truth_value'],'reproduced_tv':value,'parity':value==h['truth_value']})
    changes={}
    for suffix in ('frozen-heldout-transfer','frozen-adversarial','new-challenge','new-independent-games'):
        a=read_gzip(OUT/f'C3-exposure-{suffix}.json.gz');b=read_gzip(OUT/f'C3-induction-{suffix}.json.gz')
        changes[suffix]=[{'fixture':x['fixture'],'move':x['move'],'before':x['classification'],'after':y['classification']} for x,y in zip(a['rows'],b['rows']) if x['classification']!=y['classification']]
    write_json(OUT/'induction.json',{'cycle2_reproduction':original,'cycle3_hypotheses':model.induction,'classification_changes':changes,
               'diagnosis':'The same antecedents have direct revision evidence with higher confidence. Induction remains an alternative, never independent evidence to revise into its source. Its Truth_w2c(sBC*cBC*cBA) confidence is at most 0.5 for valid STVs. No classification benefit is forced.',
               'population':'First motif observation per (piece, dependence group), training rows only. Distance subgroups use measured N,A,B,C,BA,BC. No claim of unbiased chess population or validated cross-piece induction.'})
    # Conservative sparse training curves: actual independent evidence groups.
    train_rows=[r for r in dataset['examples'] if r['split']=='train'];groups=list(dict.fromkeys(r['dependence_group'] for r in train_rows))
    curves=[]
    for n in (1,2,4,8):
        selected=groups[:n]
        with tempfile.TemporaryDirectory(prefix='pln-c3-curve-') as tmp:
            m=train([r for r in train_rows if r['dependence_group'] in selected],options={'induction':False},runtime=runtime,ledger_path=Path(tmp)/'events')
        result=evaluate(dataset,m,'challenge',runtime)
        curves.append({'groups':n,'group_ids':selected,'records':m.training_report['records'],'model_version':m.version,'metrics':result['metrics']})
    write_json(OUT/'learning-curves.json',{'order':'Fixed original training ledger order, no held-out selection','curves':curves})
    # Full proof parity over different piece counts and temporal geometries.
    original_fixture=next(p for p in read_json(ROOT/'fixtures/dataset.json')['positions'] if p['id']=='game-0')
    fixtures=[original_fixture]+[next(p for p in dataset['positions'] if p['id']==name) for name in
                                ('challenge-double-check','challenge-castle-transit','independent-games-0')]
    benchmarks=[]
    for fixture in fixtures:
        options=Cycle3Options(timeout_seconds=180,max_native_invocations=50000)
        results={};session=None
        for mode in ('reference','cold','warm'):
            if mode!='warm':session=NativeSession(runtime,mode!='reference')
            results[mode]=infer_moves(fixture['fen'],model,options,runtime,session=session)
        parity=results['reference']['candidates']==results['cold']['candidates']==results['warm']['candidates']
        assert parity and not any(r['truncated'] for r in results.values())
        benchmarks.append({'fixture':fixture,'candidates':len(results['cold']['candidates']),'full_candidate_and_proof_parity':parity,
                           'semantic_digest':digest(results['cold']['candidates']),
                           'runs':{name:{k:r[k] for k in ('native_invocations','scheduled_invocations','cache_hits','elapsed_seconds','cache_entries','proof_bytes_estimate')} for name,r in results.items()}})
    write_json(OUT/'benchmark.json',{'corpus':benchmarks,'rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'checkpoint_bytes':(OUT/'C3-full-model.json').stat().st_size,'evidence_count':model.training_report['records'],
               'cache_keys':'Pinned runtime manifest, grammar, full checkpoint/evidence/variant, observed state identity, options, exact expression and dependency identities.',
               'limits':'Proof bytes are a conservative serialized-input estimate; cache has an entry cap. Process RSS is measured, not OS-enforced.'})
    print('RESEARCH proofs, induction, learning curves and full parity complete',flush=True)
