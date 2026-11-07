"""Cycle 7 evaluation: bounded backoff, versioned proof labels and full DAG."""
from collections import Counter
import statistics,time
import chess
from pln_chess.common import digest
from pln_chess.domain import Position,inside
from pln_chess.hypotheses import candidates
from pln_chess.cycle7.inference import infer_moves,Cycle7Options,Session
from evaluation.cycle4 import root_cause,bootstrap,proof_depth
from evaluation.cycle3 import tags
from evaluation.experiments import summarize
from evaluation.cycle7_io import pack

def metric_rows(rows):return [{**r,'classification':r['legacy_classification']} for r in rows]

def evaluate(dataset,model,split,runtime,output=None,options=None):
    version=model.version
    options=options or Cycle7Options(mode='operational');rows=[];positions=[];proofs=[];proof_index={};decisions={};session=Session(runtime)
    for fixture in dataset['positions']:
        if fixture['split']!=split:continue
        pos=Position.from_fen(fixture['fen']);moves={m.notation:m for m in candidates(pos)}
        result=infer_moves(pos,model,options,runtime,session=session)
        expected={m.uci() for m in chess.Board(pos.fen()).legal_moves}
        for item in result['candidates']:
            move=moves[item['move']];label=move.notation in expected;categories=tags(pos,move,label)
            refs=[]
            hashes=item.get('proof_dag_refs') or [digest(n) for n in item['proof_trace']]
            for key,node in zip(hashes,item['proof_trace']):
                if key not in proof_index:proof_index[key]=len(proofs);proofs.append(node)
                refs.append(proof_index[key])
            decision=item['decision_node'];decisions[decision['id']]=decision
            rows.append({'fixture':fixture['id'],'family':fixture['family'],'source_game':fixture.get('source_game'),'fen':fixture['fen'],
                'move':move.notation,'candidate_id':move.id,'piece':item['piece'],'split':split,'label':label,
                'classification':item['classification'],'legacy_classification':item['legacy_classification'],'mode':item['mode'],
                'truth_value':item['raw_stv'],'local_truth_value':item['local_admissibility_truth_value'],
                'proof_status':item['proof_status'],'backoff':item['backoff'],'legacy_proof_status':item['legacy_proof_status'],'status':item['status'],'proof_complete':item['proof_complete'],
                'self_check':'self-check' in categories,'tags':categories,'destination_exists':inside(move.end),
                'root_cause':root_cause({**item,'classification':item['legacy_classification']},label,move,pos,categories),
                'proof_id':digest(item['proof_trace']),'proof_refs':refs,'decision_ref':decision['id'],
                'rule_ids':item['matched_rule_ids'],'native_rule_ids':item['native_rule_ids'],'evidence_ids':item['evidence_ids'],
                'dependence_groups':item['dependence_groups'],'evidence_channels':item['evidence_channels'],
                'observation_sources':item['observation_sources'],'model_version':version,'runtime_version':runtime.version,
                'proof_depth':proof_depth(item['proof_trace']),'abstention_reason':item['abstention_reason'],'mode_comparison':item['mode_comparison']})
        predicted={i['move'] for i in result['candidates'] if i['classification']=='supported-legal'}
        positions.append({'fixture':fixture['id'],'family':fixture['family'],'source_game':fixture.get('source_game'),
            'exact':predicted==expected,'expected':sorted(expected),'predicted':sorted(predicted),'elapsed':result['elapsed_seconds'],
            **{k:result[k] for k in ('elapsed_seconds','native_invocations','grounded_atoms','truncated','error','scheduled_invocations','cache_hits','proof_bytes_estimate')}})
    mr=metric_rows(rows);metrics=summarize(mr,positions)
    metrics.update(false_illegal=sum(r['label'] and r['classification']=='contradicted' for r in mr),unknown=sum(r['classification']=='unknown' for r in mr),
        incomplete=sum(r['classification']=='incomplete' for r in mr),empty_terminal_exact=sum(p['exact'] and not p['expected'] for p in positions),
        nonempty_exact=sum(p['exact'] and bool(p['expected']) for p in positions),bootstrap=bootstrap(mr,positions),
        classification_counts=dict(Counter(r['classification'] for r in rows)),
        in_board_only=summarize([r for r in mr if r['destination_exists']],positions),
        per_piece={p:summarize([r for r in mr if r['piece']==p],[]) for p in sorted({r['piece'] for r in mr})},
        per_family={p:summarize([r for r in mr if r['family']==p],[]) for p in sorted({r['family'] for r in mr})})
    metrics['strength_confidence']={cls:{field:{'min':min(v),'max':max(v),'mean':statistics.mean(v)} for field in ('strength','confidence') if (v:=[r['truth_value'][field] for r in rows if r['classification']==cls])} for cls in metrics['classification_counts']}
    report={'dataset_hash':dataset['hash'],'model_version':version,'runtime_version':runtime.version,'mode':options.mode,'split':split,
        'metrics':metrics,'rows':rows,'positions':positions,'native_proof_dag':proofs,'policy_decisions':decisions,
        'thresholds':vars(options),'oracle_scope':'Training/evaluation boundary only. Mode inference receives no labels.',
        'proof_dag_encoding':'ordered-interned-v1','proof_export':'Lossless ordered interned native nodes. Ordered per-candidate refs reconstruct complete original proof_trace; policy nodes are explicitly non-native.'}
    if output:pack(output,report)
    return report
