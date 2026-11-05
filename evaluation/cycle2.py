"""Identical-split comparisons, diagnostics, uncertainty, and scheduling parity."""
import math,random,resource,time,statistics
import chess
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position,inside
from pln_chess.api import infer_moves,explain_move,find_move
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle2.model import HierarchicalModel
from pln_chess.cycle2.native import NativeSession
from pln_chess.cycle2.inference import infer_moves as hierarchical_infer
from evaluation.experiments import summarize,fit_calibrator,score_calibration


def uncertainty(rows,positions):
    rng=random.Random(314159);groups={p['fixture']:[r for r in rows if r['fixture']==p['fixture']] for p in positions};keys=list(groups)
    samples={'precision':[],'recall':[]}
    for _ in range(300):
        sample=[r for key in rng.choices(keys,k=len(keys)) for r in groups[key]] if keys else []
        tp=sum(r['label'] and r['classification']=='supported' for r in sample);fp=sum(not r['label'] and r['classification']=='supported' for r in sample);total=sum(r['label'] for r in sample)
        if tp+fp:samples['precision'].append(tp/(tp+fp))
        if total:samples['recall'].append(tp/total)
    return {'method':'300 deterministic position-cluster bootstrap resamples; exploratory, families may remain correlated',
            **{k:[sorted(v)[int(.025*(len(v)-1))],sorted(v)[int(.975*(len(v)-1))]] if v else None for k,v in samples.items()}}


def evaluate(dataset,model,split,runtime=None,output=None):
    runtime=runtime or Runtime(timeout=120);rows=[];positions=[]
    session=NativeSession(runtime) if model.schema==2 else None
    train_fens={r['fen'] for r in dataset['examples'] if r['split']=='train'}
    for fixture in dataset['positions']:
        if fixture['split']!=split:continue
        pos=Position.from_fen(fixture['fen']);moves={m.notation:m for m in candidates(pos)}
        result=hierarchical_infer(pos,model,runtime=runtime,session=session) if model.schema==2 else infer_moves(pos,model,runtime=runtime)
        for item in result['candidates']:
            move=moves[item['move']];board=chess.Board(pos.fen())
            try: label=chess.Move.from_uci(move.notation) in board.legal_moves
            except ValueError:label=False
            after=pos.successor(move);self_check=False
            if after:
                b=chess.Board(after.fen());king=b.king(pos.turn=='White')
                self_check=king is not None and b.is_attacked_by(pos.turn!='White',king)
            chosen=item.get('chosen_hypothesis_id');h=model.hypotheses.get(chosen,{})
            rows.append({'fixture':fixture['id'],'move':move.notation,'piece':item['piece'],'label':label,'self_check':self_check,
                         'classification':item['classification'],'truth_value':item['legal_move_truth_value'],'destination_exists':inside(move.end),
                         'tier':h.get('tier'),'chosen_hypothesis':chosen,'exact_context_match':any(r['tier']==6 and r['id'] in model.hypotheses for r in item['observations'].get('relations',[])) if model.schema==2 else None,
                         'proof_nodes':len(item['proof_trace']),'proof_depth':proof_depth(item['proof_trace']),
                         'attack_conflicts':len(item.get('exposure_conflicts',[])),'new_board':pos.fen() not in train_fens})
        expected={m.uci() for m in chess.Board(pos.fen()).legal_moves};predicted={i['move'] for i in result['candidates'] if i['classification']=='supported'}
        positions.append({'fixture':fixture['id'],'family':fixture['family'],'exact':expected==predicted,'expected':sorted(expected),'predicted':sorted(predicted),
                          'elapsed':result['elapsed_seconds'],'native_invocations':result['native_invocations'],'scheduled_invocations':result['scheduled_invocations'],
                          'grounded_atoms':result['grounded_atoms'],'truncated':result['truncated'],'error':result['error']})
    metrics=summarize(rows,positions);metrics['in_board']=summarize([r for r in rows if r['destination_exists']],positions)
    metrics['per_piece']={p:summarize([r for r in rows if r['piece']==p],[]) for p in sorted({r['piece'] for r in rows})}
    metrics['by_tier']={str(t):summarize([r for r in rows if r['tier']==t],[]) for t in {r['tier'] for r in rows}}
    metrics['unseen_exact_context']=summarize([r for r in rows if r['exact_context_match'] is False],[])
    metrics['uncertainty']=uncertainty(rows,positions)
    metrics['self_check_false_legal_rate']=sum(r['self_check'] and not r['label'] and r['classification']=='supported' for r in rows)/max(1,sum(r['self_check'] and not r['label'] for r in rows))
    metrics['proof_depth_mean']=statistics.mean(r['proof_depth'] for r in rows) if rows else 0
    metrics['peak_process_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report={'split':split,'scope':'full bounded candidate sets; warm pure-native expression cache within each split for schema 2',
            'dataset_hash':dataset['hash'],'model_version':model.version,'metrics':metrics,'rows':rows,'positions':positions}
    if output:write_json(output,report)
    return report


def proof_depth(trace):
    depths={}
    for node in trace:depths[node['id']]=1+max([depths[p['node']] for p in node['premises'] if 'node' in p] or [0])
    return max(depths.values(),default=0)


def baselines(dataset):
    """Empirical frequency baselines only in the isolated evaluation tree."""
    result={}
    for variant in ('geometry','absolute'):
        def key(row):
            p=Position.from_fen(row['fen']);m=find_move(p,row['move']);kind=p.at(m.start).kind
            if variant=='absolute':return kind,m.start,m.end,m.promotion
            from pln_chess.cycle2.descriptors import descriptors
            return digest(descriptors(p,m)['relations'][1]['descriptor'])
        counts={}
        for r in dataset['examples']:
            if r['split']=='train' and r['training_eligible']:counts.setdefault(key(r),[]).append(r['label'])
        result[variant]={}
        for split in sorted({p['split'] for p in dataset['positions']}):
            rows=[];timings={}
            for r in dataset['examples']:
                if r['split']!=split:continue
                started=time.perf_counter()
                values=counts.get(key(r),[]);s=sum(values)/len(values) if values else .5
                p=Position.from_fen(r['fen']);m=find_move(p,r['move']);after=p.successor(m);self_check=False
                if after:
                    board=chess.Board(after.fen());king=board.king(p.turn=='White')
                    self_check=king is not None and board.is_attacked_by(p.turn!='White',king)
                rows.append({'fixture':r['position_fixture'],'move':r['move'],'piece':p.at(m.start).kind,'label':r['label'],
                             'self_check':self_check,'destination_exists':inside(m.end),
                             'classification':'supported' if s>=.8 else 'contradicted' if s<=.2 else 'unknown'})
                timings[r['position_fixture']]=timings.get(r['position_fixture'],0)+time.perf_counter()-started
            positions=[]
            for fixture,elapsed in timings.items():
                group=[r for r in rows if r['fixture']==fixture]
                positions.append({'fixture':fixture,'elapsed':elapsed,'exact':{r['move'] for r in group if r['label']}=={r['move'] for r in group if r['classification']=='supported'},'truncated':False})
            metrics=summarize(rows,positions)
            metrics['per_piece']={piece:summarize([r for r in rows if r['piece']==piece],[]) for piece in sorted({r['piece'] for r in rows})}
            metrics['in_board']=summarize([r for r in rows if r['destination_exists']],positions)
            metrics['self_check_false_legal_rate']=sum(r['self_check'] and not r['label'] and r['classification']=='supported' for r in rows)/max(1,sum(r['self_check'] and not r['label'] for r in rows))
            metrics['uncertainty']=uncertainty(rows,positions)
            result[variant][split]=metrics
    return {'scope':'B6 evaluation-only empirical baselines; not native PLN and not available to production inference','results':result}


def parity_and_benchmark(model,output=None):
    dataset=read_json(ROOT/'fixtures/dataset.json');fixture=next(p for p in dataset['positions'] if p['id']=='game-0');runtime=Runtime(timeout=180)
    runs=[];results={}
    for mode,optimized in [('reference',False),('cold',True),('warm',True)]:
        if mode!='warm':session=NativeSession(runtime,optimized)
        result=hierarchical_infer(fixture['fen'],model,runtime=runtime,session=session);results[mode]=result
        runs.append({k:result[k] for k in ('native_invocations','scheduled_invocations','cache_hits','elapsed_seconds','truncated')}|{'mode':mode})
    def semantics(r):
        return [{k:i.get(k) for k in ('move','classification','legal_move_truth_value','movement_truth_value','matched_rule_ids','evidence_ids','proof_trace')} for i in r['candidates']]
    parity=semantics(results['reference'])==semantics(results['cold'])==semantics(results['warm'])
    assert parity and all(not r['truncated'] for r in runs)
    result={'fixture':fixture,'candidates':len(results['cold']['candidates']),'parity':parity,'compared':'Full TVs, classifications, native logical nodes, rule IDs, and evidence lineage',
            'runs':runs,'cold_speedup':runs[0]['elapsed_seconds']/runs[1]['elapsed_seconds'],'call_reduction':runs[0]['native_invocations']/max(1,runs[1]['native_invocations']),
            'warm_mode':'In-memory memoized pure native expression results; no long-lived PeTTa process or Python TV calculation',
            'checkpoint_bytes':(ROOT/'artifacts/cycle2/B2-model.json').stat().st_size,
            'stage_profile':{op:sum(t['operator']==op for i in results['cold']['candidates'] for t in i['proof_trace']) for op in ('Truth_ModusPonens','Truth_Negation','BestConfidenceCandidate')}}
    if output:write_json(output,result)
    return result


def demonstrations(dataset,model,output=None):
    runtime=Runtime();proofs={}
    from pln_chess.evidence import Ledger
    evidence={r['evidence_id']:r['payload'] for r in Ledger(ROOT/'artifacts/cycle2/evidence.jsonl').records()}
    for name in ('locality-source','translated','irrelevant-knight','color-flip','c1-rook-pinned','c1-en-passant-opens-ray','c1-castle-through-attack'):
        fixture=next(p for p in dataset['positions'] if p['id']==name)
        proofs[name]=explain_move(fixture['fen'],fixture['focus_move'],model,runtime=runtime)
    a=proofs['locality-source']['candidate'];b=proofs['irrelevant-knight']['candidate']
    invariance={k:a.get(k)==b.get(k) for k in ('movement_hypothesis_id','movement_truth_value')}
    examples=[]
    for piece in ('Rook','Bishop','Queen'):
        for fixture in dataset['positions']:
            if fixture['split']!='heldout-transfer' or 'ray' not in fixture['id']:continue
            p=Position.from_fen(fixture['fen']);move=find_move(p,fixture['focus_move'])
            if p.at(move.start).kind!=piece:continue
            r=explain_move(p,move,model,runtime=runtime);c=r['candidate'];key=c['chosen_hypothesis_id']
            if c['classification'] not in ('supported','contradicted') or not key:continue
            if any(h['tier']==6 and h['id'] in model.hypotheses for h in c['observations']['relations']):continue
            h=model.hypotheses[key]
            if h['tier']!=4:continue
            if piece=='Rook' and not h['descriptor'].get('ray_contents'):continue
            proofs[fixture['id']]=r
            examples.append({'test_fixture':fixture,'piece':piece,'hypothesis':h,'truth_value':c['legal_move_truth_value'],'classification':c['classification'],
                             'training_examples':[{'evidence_id':eid,'input':evidence[eid]['input'],'label':evidence[eid]['label'],
                                                   'dependence_group':evidence[eid]['dependence_group']} for eid in h['evidence_ids'][:3]],
                             'novelty':'Held-out generative family, longer ray, mixed opponent context, no exact-context rule; tier 4 distance-agnostic occupancy/destination relation.'})
            break
    report={'locality_invariance':invariance,'proofs':proofs,'generalization_examples':examples}
    if output:write_json(output,report)
    return report
