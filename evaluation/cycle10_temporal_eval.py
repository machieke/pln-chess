"""Full-candidate evaluation with supplied game histories, outside production."""
from dataclasses import asdict,replace
from collections import Counter
from pln_chess.common import digest
from evaluation.cycle8 import evaluate
from evaluation.cycle9_analysis import metrics
from evaluation.cycle7_io import pack


def evaluate_temporal(dataset,model,split,runtime,options,output=None):
    from pln_chess.cycle10.temporal import replay_game,native_options
    games={g['id']:g for g in dataset['games']};rows=[];positions=[];nodes=[];index={};decisions={};histories=[]
    for fixture in dataset['positions']:
        if fixture['split']!=split:continue
        if fixture.get('source_game') not in games:raise ValueError('Actual game history required for external temporal evaluation')
        history=replay_game(games[fixture['source_game']],fixture['ply'],model.version,runtime.version)
        assert history['resulting_fen']==fixture['fen']
        configured=native_options(history,options)
        report=evaluate({**dataset,'positions':[fixture]},model,split,runtime,configured)
        mapping={}
        for old,node in enumerate(report['native_proof_dag']):
            key=digest(node)
            if key not in index:index[key]=len(nodes);nodes.append(node)
            mapping[old]=index[key]
        for row in report['rows']:
            row={**row,'proof_refs':[mapping[i] for i in row['proof_refs']],
                 'temporal_transport_id':history['id']}
            assert digest([nodes[i] for i in row['proof_refs']])==row['proof_id'];rows.append(row)
        positions.extend({**p,'temporal_transport_id':history['id']} for p in report['positions']);decisions.update(report['policy_decisions'])
        histories.append(dict(fixture=fixture['id'],transport=history))
    summary=metrics(rows,positions)
    summary.update(classification_counts=dict(Counter(r['classification'] for r in rows)),
        promotion_specific=metrics([r for r in rows if r['promotion']],[]),
        per_piece={p:metrics([r for r in rows if r['piece']==p],[]) for p in sorted({r['piece'] for r in rows})},
        in_board_only=metrics([r for r in rows if r['destination_exists']],positions))
    result=dict(schema=10,dataset_hash=dataset['hash'],model_version=model.version,runtime_version=runtime.version,
        mode=options.mode,split=split,metrics=summary,rows=rows,positions=positions,native_proof_dag=nodes,policy_decisions=decisions,
        thresholds=asdict(options),temporal_histories=histories,oracle_scope='Offline labels only. Production transport replays supplied events without a chess oracle.',
        scope='Same accepted model; supplied complete game prefixes replace unknown history. Positive proofs remain partial.')
    if output:pack(output,result)
    return result
