"""Common evaluator for unchanged C7 and C8, including missing observations."""
from collections import Counter
from dataclasses import asdict
from pathlib import Path
import statistics
import chess
from pln_chess.common import digest
from pln_chess.domain import Position, inside
from pln_chess.hypotheses import candidates
from evaluation.experiments import summarize
from evaluation.cycle3 import tags
from evaluation.cycle4 import root_cause, bootstrap, proof_depth
from evaluation.cycle7_io import pack


def evaluate(dataset, model, split, runtime, options, output=None):
    if model.schema==8:
        from pln_chess.cycle8.inference import infer_moves,Session
    else:
        from pln_chess.cycle7.inference import infer_moves,Session
    session=Session(runtime);rows=[];positions=[];proofs=[];proof_index={};decisions={};version=model.version
    for fixture in dataset['positions']:
        if fixture['split']!=split:continue
        pos=Position.from_fen(fixture['fen'],unknown_squares=tuple(tuple(s) for s in fixture.get('unknown_squares',[])))
        moves={m.notation:m for m in candidates(pos)}
        result=infer_moves(pos,model,options,runtime,session=session)
        expected={m.uci() for m in chess.Board(pos.fen()).legal_moves}
        for item in result['candidates']:
            move=moves[item['move']];label=move.notation in expected;categories=tags(pos,move,label);refs=[]
            for node in item['proof_trace']:
                identifier=digest(node)
                if identifier not in proof_index:proof_index[identifier]=len(proofs);proofs.append(node)
                refs.append(proof_index[identifier])
            decision=item['decision_node'];decisions[decision['id']]=decision
            row={'fixture':fixture['id'],'family':fixture['family'],'source_game':fixture.get('source_game'),
                'dependence_group':fixture.get('dependence_group',fixture.get('source_game') or fixture['id']),
                'fen':fixture['fen'],'unknown_squares':fixture.get('unknown_squares',[]),
                'move':move.notation,'candidate_id':move.id,'piece':item['piece'],'split':split,'label':label,
                'classification':item['classification'],'legacy_classification':item['legacy_classification'],'mode':item['mode'],
                'truth_value':item['raw_stv'],'local_truth_value':item['local_admissibility_truth_value'],
                'proof_status':item['proof_status'],'proof_complete':item['proof_complete'],
                'positive_proof_complete':item['positive_proof_complete'],'status':item['status'],
                'backoff':item['backoff'],'promotion':move.promotion,'promotion_transition':item.get('promotion_transition'),
                'promotion_selection':item.get('promotion_selection'),
                'self_check':'self-check' in categories,'tags':categories,'destination_exists':inside(move.end),
                'root_cause':root_cause({**item,'classification':item['legacy_classification']},label,move,pos,categories),
                'proof_id':digest(item['proof_trace']),'proof_refs':refs,'decision_ref':decision['id'],
                'rule_ids':item['matched_rule_ids'],'native_rule_ids':item['native_rule_ids'],
                'evidence_ids':item['evidence_ids'],'dependence_groups':item['dependence_groups'],
                'evidence_channels':item['evidence_channels'],'observation_sources':item['observation_sources'],
                'typed_premises':item['typed_premises'],'model_version':version,'runtime_version':runtime.version,
                'proof_depth':proof_depth(item['proof_trace']),'abstention_reason':item['abstention_reason']}
            rows.append(row)
        predicted={i['move'] for i in result['candidates'] if i['classification']=='supported-legal'}
        positions.append({'fixture':fixture['id'],'family':fixture['family'],'source_game':fixture.get('source_game'),
            'dependence_group':fixture.get('dependence_group',fixture.get('source_game') or fixture['id']),
            'exact':predicted==expected,'expected':sorted(expected),'predicted':sorted(predicted),'elapsed':result['elapsed_seconds'],
            **{k:result[k] for k in ('elapsed_seconds','native_invocations','grounded_atoms','truncated','error','scheduled_invocations','cache_hits','proof_bytes_estimate')}})
    def metrics_for(selected,selected_positions):
        legacy=[{**r,'classification':r['legacy_classification']} for r in selected]
        metrics=summarize(legacy,selected_positions)
        metrics.update(false_illegal=sum(r['label'] and r['classification']=='supported-illegal' for r in selected),
            unknown=sum(r['classification']=='unknown' for r in selected),incomplete=sum(r['classification']=='incomplete' for r in selected))
        return metrics
    metrics=metrics_for(rows,positions)
    metrics.update(classification_counts=dict(Counter(r['classification'] for r in rows)),
        promotion_specific=metrics_for([r for r in rows if r['promotion']],[]),
        per_piece={p:metrics_for([r for r in rows if r['piece']==p],[]) for p in sorted({r['piece'] for r in rows})},
        per_family={p:metrics_for([r for r in rows if r['family']==p],[q for q in positions if q['family']==p]) for p in sorted({r['family'] for r in rows})},
        in_board_only=metrics_for([r for r in rows if r['destination_exists']],positions),
        empty_terminal_exact=sum(p['exact'] and not p['expected'] for p in positions),
        nonempty_exact=sum(p['exact'] and bool(p['expected']) for p in positions),
        proof_coverage=dict(Counter(r['proof_status'] for r in rows)))
    report={'schema':8,'dataset_hash':dataset['hash'],'model_version':version,'runtime_version':runtime.version,
        'mode':options.mode,'split':split,'metrics':metrics,'rows':rows,'positions':positions,
        'native_proof_dag':proofs,'policy_decisions':decisions,'thresholds':asdict(options),
        'proof_dag_encoding':'ordered-interned-v1','oracle_scope':'Offline labels; no reference labels passed to inference.',
        'missing_observations':'Unknown squares are applied to Position before inference, not only attached as evaluation metadata.'}
    if output:pack(output,report)
    return report
