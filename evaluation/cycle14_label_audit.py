"""Inspect all historical unknowns and execute raw-wire adapter fixtures."""
import argparse
from collections import Counter
import inspect
from pathlib import Path

import chess
import chess.engine

from pln_chess.common import ROOT,digest,read_json,write_json
from scripts.cycle9_baseline import sha
from training.cycle14_reference import RawEngine,board_from_history,classify_tier,parse_info


def legacy_causes(record):
    causes=[]
    evaluations=record['evaluations']
    if any(len(e['candidates'])!=2 for e in evaluations):causes.append('missing-candidate-analysis')
    if any(c.get('lowerbound') or c.get('upperbound') for e in evaluations for c in e['candidates']):
        causes.append('stored-score-bound')
    if any(c['score']['mate'] is not None for e in evaluations for c in e['candidates']):
        causes.append('mate-order-requires-audit')
    if not causes:causes.append('budget-disagreement-or-insufficient-margin')
    if record.get('horizon')==3 and 'stored-score-bound' in causes:
        causes.append('odd-horizon-bound-perspective-not-reversed-in-c13-adapter')
    return causes


def run(out):
    out=Path(out);target=out/'reference-audit';target.mkdir(parents=True,exist_ok=True)
    reference=read_json(ROOT/'artifacts/cycle13/sources/stockfish-source.json')
    binary=ROOT/reference['binary_path'];assert sha(binary)==reference['binary_sha256']
    pairs={r['id']:r for r in read_json(ROOT/'artifacts/cycle13/datasets/source-pairs.json')['records']}
    historical=read_json(ROOT/'artifacts/cycle13/datasets/reference-labels.json')['records']
    temporal=read_json(ROOT/'artifacts/cycle13/datasets/temporal-labels.json')['records']
    unknown=[r for r in historical if r['split']=='test' and r['label']=='unknown'];assert len(unknown)==41
    census=[]
    for row in unknown+[r for r in temporal if r['label']=='unknown']:
        census.append(dict(id=row['id'],horizon=row.get('horizon',1),original_label=row['label'],
            original_evidence_id=row['evidence_id'],original_reason=row['reason'],
            cause_flags=legacy_causes(row),original_record_sha256=digest(row),
            raw_wire_transcript_available=False,
            scope='Cause flags from preserved aggregate records and source inspection; fresh wire evidence is separately identified'))
    write_json(target/'original-unknown-census.json',dict(records=census,immediate_test_unknown=41,
        temporal_unknown=sum(r['label']=='unknown' for r in temporal),
        cause_counts=dict(Counter(c for r in census for c in r['cause_flags']))))
    api_source=inspect.getsource(chess.engine.AnalysisResult.post)
    (target/'pinned-analysis-aggregation.py.txt').write_text(api_source)
    fixtures=[]
    with RawEngine(binary) as engine:
        write_json(target/'engine-initialization.json',dict(transcript=engine.initialization,
            binary_sha256=sha(binary),reference_manifest_sha256=sha(ROOT/'artifacts/cycle13/sources/stockfish-source.json')))
        for original in sorted(unknown,key=lambda r:r['id']):
            row=pairs[original['id']];path=target/'raw'/f"{row['id']}.json"
            identity=dict(pair_sha256=digest(row),engine_sha256=sha(binary),
                adapter_sha256=sha(ROOT/'training/cycle14_reference.py'),method='historical-two-root-MultiPV',node_budgets=[20000,80000])
            if path.exists():
                result=read_json(path);assert result['identity']==identity
                fixtures.append(result);continue
            actor=board_from_history(row['history'],row['fen']).turn
            analyses=[];comparisons=[];stale=[]
            for nodes in (20000,80000):
                raw=engine.analyze(row['history'],roots=row['moves'],nodes=nodes,actor=actor,expected_fen=row['fen'],multipv=2)
                analyses.append(raw)
                candidates={side:raw['candidates'].get(move) for side,move in zip(('A','B'),row['moves'])}
                comparisons.append(dict(candidates=candidates,termination=raw['termination'],history_verified=raw['history_verified']))
                # Reproduce the pinned library's update policy over the exact
                # same wire records, so differences are parsing, not searches.
                aggregate={}
                for event in raw['transcript']:
                    if event['direction']!='received' or not event['line'].startswith('info '):continue
                    parsed=chess.engine._parse_uci_info(event['line'][5:],board_from_history(row['history']),chess.engine.INFO_ALL)
                    if parsed:aggregate.setdefault(parsed.get('multipv',1),{}).update(parsed)
                for info in aggregate.values():
                    pv=info.get('pv')
                    if not pv:continue
                    fresh=raw['candidates'].get(pv[0].uci())
                    if fresh and fresh['score']['bound']=='unflagged' and (info.get('lowerbound') or info.get('upperbound')):
                        stale.append(dict(nodes=nodes,candidate=pv[0].uci(),fresh_bound='unflagged',
                            aggregate_lower=bool(info.get('lowerbound')),aggregate_upper=bool(info.get('upperbound'))))
            label,reason=classify_tier(comparisons)
            result=dict(id=row['id'],identity=identity,original_label=original['label'],
                original_evidence_id=original['evidence_id'],same_search_wire_corrected_label=label,
                corrected_reason=reason,stale_bound_instances=stale,analyses=analyses,
                original_label_preserved=True,method='MultiPV replay diagnostic; separate-root primary supervision is a different registered method')
            write_json(path,result);fixtures.append(result)
            print('RAW ADAPTER AUDIT',row['id'],label,len(stale),flush=True)
    write_json(target/'verified.json',dict(passed=True,original_immediate_unknown=41,
        original_temporal_unknown=sum(r['label']=='unknown' for r in temporal),raw_replayed_pairs=len(fixtures),
        raw_replayed_searches=2*len(fixtures),stale_bound_pairs=sum(bool(r['stale_bound_instances']) for r in fixtures),
        corrected_multipv_labels=dict(Counter(r['same_search_wire_corrected_label'] for r in fixtures)),
        fixtures=[dict(id=r['id'],sha256=sha(target/'raw'/f"{r['id']}.json")) for r in fixtures],
        chess_version=chess.__version__,engine_module_sha256=sha(chess.engine.__file__),
        aggregate_source_sha256=sha(target/'pinned-analysis-aggregation.py.txt'),
        original_raw_wire_available=False,original_labels_mutated=False,
        finding='Pinned AnalysisResult.post merges updates without clearing missing bound flags; fresh raw-wire fixtures isolate this behavior. '
            'No claim that the unavailable original wire transcript was independently inspected.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    run(parser.parse_args().out)
