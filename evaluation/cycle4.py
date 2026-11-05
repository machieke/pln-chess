"""Complete candidate scoring and complete diagnostic case ledgers. Oracle here only."""
from collections import Counter
from pathlib import Path
import resource,random,statistics
import chess
from pln_chess.common import digest,write_json
from pln_chess.domain import Position,inside
from pln_chess.hypotheses import candidates
from pln_chess.cycle4.inference import infer_moves,Cycle4Options
from pln_chess.cycle3.native import NativeSession
from evaluation.cycle3 import infer as previous_infer,tags
from evaluation.experiments import summarize
from scripts.cycle4_baseline import pack


def root_cause(item,label,move,position,categories):
    """Mutually exclusive primary cause with retained secondary evaluation tags."""
    if item['classification']=='incomplete':return 'scheduler-budget'
    if move.effect=='en-passant':return 'en-passant-discovered-attack' if 'self-check' in categories else 'en-passant-history'
    if move.effect=='castle':return 'castling-history-transit'
    if not inside(move.end):return 'board-boundary'
    if move.promotion:return 'promotion'
    if 'self-check' in categories:
        board=chess.Board(position.fen())
        if len(board.checkers())>1:return 'double-check'
        return 'attacked-destination' if item['piece']=='King' else 'pin-exposure'
    c=item['observations']['context']
    if c['destination']=='Friendly':return 'friendly-destination'
    if any(v not in ('Empty','Boundary') for v in c['intermediate']):return 'blocker-composition'
    if not item.get('chosen_hypothesis_id'):return 'geometry-abstraction-mismatch' if item.get('matched_hypotheses') else 'missing-movement-prior'
    if item.get('conflicting_hypotheses'):return 'contradictory-evidence'
    if item['classification']=='unknown':return 'insufficient-evidence'
    return 'other'


def bootstrap(rows,positions,draws=300):
    rng=random.Random(424242);groups={}
    for p in positions:groups.setdefault(p['source_game'] or p['fixture'],[]).append(p['fixture'])
    keys=sorted(groups);by={p['fixture']:[r for r in rows if r['fixture']==p['fixture']] for p in positions}
    samples={k:[] for k in ('precision','recall','coverage','exact_move_set_accuracy')}
    for _ in range(draws):
        ids=[pid for _ in keys for pid in groups[rng.choice(keys)]]
        selected=[r for pid in ids for r in by[pid]]
        met=summarize(selected,[p for pid in ids for p in positions if p['fixture']==pid])
        for k in samples:
            if met[k] is not None:samples[k].append(met[k])
    return {'method':'Percentile bootstrap of source games (positions for non-game motifs); exploratory, 300 draws.',
            'independent_clusters':len(keys),'interval95':{k:[sorted(v)[int(.025*len(v))],sorted(v)[min(len(v)-1,int(.975*len(v)))]] if v else None for k,v in samples.items()}}


def evaluate(dataset,model,split,runtime,output=None,options=None,diagnostics=False):
    options=options or Cycle4Options(max_proof_bytes=1024*1024*1024 if not model.training_report.get('dependence_aware',True) else 64*1024*1024)
    rows=[];positions=[];cases=[];proofs={};session=NativeSession(runtime)
    run=infer_moves if model.schema==4 else previous_infer
    for fixture in dataset['positions']:
        if fixture['split']!=split:continue
        pos=Position.from_fen(fixture['fen']);moves={m.notation:m for m in candidates(pos)}
        result=run(pos,model,runtime=runtime,session=session,options=options)
        expected={m.uci() for m in chess.Board(pos.fen()).legal_moves}
        for item in result['candidates']:
            move=moves[item['move']];label=move.notation in expected;categories=tags(pos,move,label)
            proof=digest(item['proof_trace']);cls=item['classification']
            row={'fixture':fixture['id'],'family':fixture['family'],'source_game':fixture.get('source_game'),
                 'split':split,'fen':fixture['fen'],'candidate_id':move.id,'move':move.notation,'piece':item['piece'],
                 'label':label,'classification':cls,'truth_value':item['legal_move_truth_value'],
                 'local_truth_value':item.get('local_admissibility_truth_value'), 'status':item['status'],
                 'self_check':'self-check' in categories,'tags':categories,'destination_exists':inside(move.end),
                 'root_cause':root_cause(item,label,move,pos,categories),'proof_id':proof,
                 'chosen_hypothesis':item.get('chosen_hypothesis_id'),'rule_ids':item['matched_rule_ids'],
                 'evidence_ids':item['evidence_ids'],'proof_depth':proof_depth(item['proof_trace']),
                 'abstention_reason':item['gaps'] if cls in ('unknown','incomplete') else []}
            rows.append(row)
            unresolved=cls in ('unknown','incomplete') or (label and cls!='supported') or (not label and cls=='supported')
            if diagnostics and unresolved:
                cases.append({**row,'source_target_relations':item['observations']['relations'],
                              'raw_context':item['observations']['context'],'matched_hypotheses':item.get('matched_hypotheses',[]),
                              'attack_beliefs':item.get('attack_beliefs',[]),'selection_policy':item.get('decision_policy',item.get('selection_policy'))})
                proofs[proof]=item['proof_trace']
        predicted={i['move'] for i in result['candidates'] if i['classification']=='supported'}
        positions.append({'fixture':fixture['id'],'family':fixture['family'],'source_game':fixture.get('source_game'),
            'exact':predicted==expected,'expected':sorted(expected),'predicted':sorted(predicted),
            'elapsed':result['elapsed_seconds'],'native_invocations':result['native_invocations'],'grounded_atoms':result['grounded_atoms'],
            'truncated':result['truncated'],'error':result['error'],'scheduled_invocations':result['scheduled_invocations'],
            'cache_hits':result['cache_hits'],'proof_bytes_estimate':result.get('proof_bytes_estimate'),
            'unexplored_branches':result.get('unexplored_branches',0)})
    metrics=summarize(rows,positions)
    metrics.update(false_illegal=sum(r['label'] and r['classification']=='contradicted' for r in rows),
                   unknown=sum(r['classification']=='unknown' for r in rows),incomplete=sum(r['classification']=='incomplete' for r in rows),
                   selective_risk=1-metrics['selective_accuracy'] if metrics['selective_accuracy'] is not None else None,
                   mean_proof_depth=statistics.mean(r['proof_depth'] for r in rows) if rows else 0,
                   peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    metrics['per_piece']={p:summarize([r for r in rows if r['piece']==p],[]) for p in sorted({r['piece'] for r in rows})}
    metrics['special_moves']={tag:summarize([r for r in rows if tag in r['tags']],[]) for tag in ('castling','en-passant','promotion','boundary','self-check')}
    metrics['bootstrap']=bootstrap(rows,positions)
    report={'dataset_hash':dataset['hash'],'model_version':model.version,'split':split,'metrics':metrics,'rows':rows,'positions':positions,
            'thresholds':vars(options),'cases':cases,'proofs':proofs,
            'taxonomy':dict(Counter(c['root_cause'] for c in cases).most_common()),
            'oracle_scope':'Evaluation labels only. Native inference receives Position, model and budget only.'}
    if output:pack(output,report)
    return report


def proof_depth(trace):
    depths={}
    for t in trace:depths[t['id']]=1+max((depths.get(p['node'],0) for p in t['premises'] if 'node' in p),default=0)
    return max(depths.values(),default=0)
