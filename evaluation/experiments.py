"""Metrics and evaluation-only baselines. Reference engine stays in this tree."""
from __future__ import annotations
import math
from pathlib import Path
import resource
import statistics
import time
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.api import train,explain_move,compare_transforms
from pln_chess.inference import infer_moves,Options
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from training.factory import reference_label


def quantile(values,q):
    ordered=sorted(values)
    if not ordered: return None
    return ordered[min(len(ordered)-1,math.ceil(q*len(ordered))-1)]


def summarize(rows,positions):
    tp=sum(r['label'] and r['classification']=='supported' for r in rows)
    fp=sum(not r['label'] and r['classification']=='supported' for r in rows)
    fn=sum(r['label'] and r['classification']!='supported' for r in rows)
    tn=sum(not r['label'] and r['classification']=='contradicted' for r in rows)
    predicted=sum(r['classification'] in ('supported','contradicted') for r in rows)
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    return {'candidates':len(rows),'true_positive':tp,'false_positive':fp,'false_negative_including_abstention':fn,
            'true_negative':tn,'precision':precision,'recall':recall,'f1':f1,
            'coverage':predicted/len(rows) if rows else 0,'abstention_rate':1-predicted/len(rows) if rows else 0,
            'selective_accuracy':(tp+tn)/predicted if predicted else None,
            'false_legal_rate':fp/sum(not r['label'] for r in rows) if any(not r['label'] for r in rows) else None,
            'self_check_false_legal':sum(r.get('self_check',False) and r['classification']=='supported' and not r['label'] for r in rows),
            'exact_move_set_accuracy':sum(p['exact'] for p in positions)/len(positions) if positions else None,
            'incomplete_positions':sum(p.get('truncated',False) for p in positions),
            'latency_seconds':{k:quantile([p['elapsed'] for p in positions],q) for k,q in (('p50',.5),('p95',.95),('p99',.99))},
            'native_invocations':sum(p.get('native_invocations',0) for p in positions),
            'grounded_atoms':sum(p.get('grounded_atoms',0) for p in positions)}


def evaluate(dataset,model,split='heldout-transfer',runtime=None,focus_only=False,options=None):
    runtime=runtime or Runtime(); rows=[]; positions=[]
    for fixture in dataset['positions']:
        if fixture['split']!=split: continue
        pos=Position.from_fen(fixture['fen']); move_map={m.notation:m for m in candidates(pos)}
        selection=[move_map[fixture['focus_move']]] if focus_only and fixture['focus_move'] else None
        result=infer_moves(pos,model,options,runtime,selection)
        for item in result['candidates']:
            move=move_map[item['move']]; after=pos.successor(move)
            self_check=False
            if after:
                b=chess.Board(after.fen()); king=b.king(pos.turn=='White')
                self_check=king is not None and b.is_attacked_by(pos.turn!='White',king)
            rows.append({'fixture':fixture['id'],'move':item['move'],'piece':item['piece'],
                         'label':reference_label(pos,move),'classification':item['classification'],
                         'truth_value':item['legal_move_truth_value'],'self_check':self_check,
                         'destination_exists':item['observations']['context'].get('destination_exists',True)})
        expected={m.uci() for m in chess.Board(pos.fen()).legal_moves}
        if focus_only: expected &= {m.notation for m in selection or []}
        predicted={r['move'] for r in result['candidates'] if r['classification']=='supported'}
        positions.append({'fixture':fixture['id'],'family':fixture['family'],'exact':expected==predicted,
                          'expected':sorted(expected),'predicted':sorted(predicted),'truncated':result['truncated'],
                          'elapsed':result['elapsed_seconds'],'native_invocations':result['native_invocations'],
                          'grounded_atoms':result['grounded_atoms'],'pieces':len(pos.pieces),
                          'candidate_count':len(result['candidates']),'error':result['error']})
    metrics=summarize(rows,positions)
    metrics['per_piece']={piece:summarize([r for r in rows if r['piece']==piece],[]) for piece in sorted({r['piece'] for r in rows})}
    metrics['in_board_only']=summarize([r for r in rows if r['destination_exists']],positions)
    return {'split':split,'scope':'focus moves only' if focus_only else 'complete bounded candidate sets',
            'dataset_hash':dataset['hash'],'model_version':model.version,'runtime_version':runtime.version,
            'metrics':metrics,'positions':positions,'rows':rows}


def fit_calibrator(validation):
    # Post-hoc empirical strength bins. NOT used by native inference or classification.
    buckets={}
    rows=validation['rows']; rate=sum(r['label'] for r in rows)/len(rows) if rows else .5
    for row in rows:
        b=min(9,int(row['truth_value']['strength']*10))
        buckets.setdefault(str(b),[]).append(int(row['label']))
    return {'method':'empirical decile bins of raw native strength; empty bins use validation base rate',
            'bins':{b:sum(v)/len(v) for b,v in buckets.items()},'counts':{b:len(v) for b,v in buckets.items()},
            'fallback':rate,'fit_split':'validation','warning':'Small validation sample; probabilities are exploratory and never alter raw PLN TVs.'}


def score_calibration(report,calibrator):
    rows=report['rows']; pairs=[]
    for r in rows:
        key=str(min(9,int(r['truth_value']['strength']*10)))
        pairs.append((calibrator['bins'].get(key,calibrator['fallback']),int(r['label'])))
    groups={}
    for p,y in pairs: groups.setdefault(p,[]).append(y)
    return {'mapping':calibrator,'scored_split':report['split'],
            'brier':sum((p-y)**2 for p,y in pairs)/len(pairs) if pairs else None,
            'log_loss':-sum(y*math.log(max(1e-12,p))+(1-y)*math.log(max(1e-12,1-p)) for p,y in pairs)/len(pairs) if pairs else None,
            'ece':sum(len(ys)*abs(p-sum(ys)/len(ys)) for p,ys in groups.items())/len(pairs) if pairs else None}


def absolute_baseline(dataset,split):
    counts={}
    for row in dataset['examples']:
        if row['split']!='train': continue
        p=Position.from_fen(row['fen']); m=next(m for m in candidates(p) if m.notation==row['move'])
        key=(p.at(m.start).kind,m.start,m.end,m.promotion)
        counts.setdefault(key,[]).append(row['label'])
    rows=[]
    for row in dataset['examples']:
        if row['split']!=split: continue
        p=Position.from_fen(row['fen']); m=next(m for m in candidates(p) if m.notation==row['move'])
        evidence=counts.get((p.at(m.start).kind,m.start,m.end,m.promotion),[])
        strength=sum(evidence)/len(evidence) if evidence else .5
        classification=('supported' if strength>=.8 else 'contradicted' if strength<=.2 else 'unknown') if evidence else 'unknown'
        rows.append({'label':row['label'],'classification':classification})
    return {'name':'evaluation-only absolute-square empirical baseline','metrics':summarize(rows,[])}


def ablations(dataset,output_dir,runtime=None):
    runtime=runtime or Runtime(); output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    # Focus-move ablations make the experiment reproducible on an ordinary laptop.
    # They are explicitly NOT represented as full-set held-out performance.
    focus={p['id']:p['focus_move'] for p in dataset['positions']}
    training=[r for r in dataset['examples'] if r['split']=='train' and r['move']==focus[r['position_fixture']]]
    results=[]
    for variant in ('full','geometry-only','weaker-prior','no-exposure','no-dependence','no-occupancy'):
        rows=list(training)
        # Correlated re-observations have a changed source, so ledger records them;
        # only the dependence policy distinguishes their statistical contributions.
        rows += [{**r,'source':r['source']+'/correlated-repeat','transformation_lineage':['same-observation']} for r in training]
        ledger=output_dir/f'{variant}.jsonl'
        model=train(rows,options={'variant':variant,'dependence_aware':variant!='no-dependence'},runtime=runtime,ledger_path=ledger)
        model.export(output_dir/f'{variant}-model.json')
        reports={s:evaluate(dataset,model,s,runtime,focus_only=True) for s in ('train','heldout-transfer','controlled-transfer')}
        results.append({'variant':variant,'training_records':len(rows),'native_updates':model.training_report['native_invocations'],
                        'mean_hypothesis_confidence':statistics.mean(v['positive']['confidence'] for v in model.hypotheses.values()),
                        'splits':{s:r['metrics'] for s,r in reports.items()}})
    return {'scope':'focus-move ablations; bounded categorical hypotheses, not a full chess rules learner',
            'results':results,'absolute_baseline':{s:absolute_baseline(dataset,s) for s in ('heldout-transfer','controlled-transfer')}}


def sample_efficiency(dataset,runtime=None):
    runtime=runtime or Runtime()
    from pln_chess.evidence import Ledger
    from pln_chess.learning import train as replay
    selected=[r for r in dataset['examples'] if r['position_fixture']=='transfer-source' and r['move']=='c3e3']
    ledger=ROOT/'artifacts/efficiency.jsonl'
    import tempfile,shutil
    with tempfile.TemporaryDirectory() as tmp:
        fresh=Path(tmp)/'evidence.jsonl'
        model=train(selected,ledger_path=fresh,runtime=runtime)
        shutil.copyfile(fresh,ledger)
    a=explain_move(next(p['fen'] for p in dataset['positions'] if p['id']=='transfer-target'),'d3f3',model,runtime=runtime)
    return {'scope':'one controlled relational transfer motif, not a population sample-efficiency estimate',
            'independent_examples':1,'target_truth_value':a['candidate']['legal_move_truth_value'],
            'target_classification':a['candidate']['classification'],
            'absolute_key_seen':False}


def benchmark(dataset,model,runtime=None):
    runtime=runtime or Runtime(); samples=[]
    for name in ('rook-clear','rook-pinned','game-0'):
        fixture=next(p for p in dataset['positions'] if p['id']==name)
        pos=Position.from_fen(fixture['fen'])
        for scope in ('single','full'):
            for repetition in range(3):
                selected=[next(m for m in candidates(pos) if m.notation==fixture['focus_move'])] if scope=='single' else None
                result=infer_moves(pos,model,runtime=runtime,selected_moves=selected)
                samples.append({'fixture':name,'scope':scope,'repetition':repetition,'seconds':result['elapsed_seconds'],
                                'native_invocations':result['native_invocations'],'grounded_atoms':result['grounded_atoms'],
                                'candidates':len(result['candidates']),'pieces':len(pos.pieces),'truncated':result['truncated']})
    return {'samples':samples,'latency':{scope:{f'p{int(q*100)}':quantile([s['seconds'] for s in samples if s['scope']==scope],q) for q in (.5,.95,.99)} for scope in ('single','full')},
            'peak_parent_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'peak_child_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'checkpoint_bytes':(ROOT/'artifacts/model.json').stat().st_size,
            'notes':'PeTTa cold process per batch; three repeats per position; RSS is process-wide high-water, not incremental allocation.'}
