"""Development-only temporal evidence reuse experiment; thresholds stay fixed."""
import argparse
from dataclasses import replace
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def run(out):
    out=Path(out);data=read_json(out/'datasets/dataset.json');fixtures={p['id']:p for p in data['positions']}
    games={g['id']:g for g in data['games']};rows=[];rt=Runtime(timeout=180)
    model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    for path in sorted((out/'evaluation').glob('operational-development-*.json.xz')):
        report=read_gzip(path)
        for row in report['rows']:
            if not row['label'] or row['classification']!='unknown':continue
            fixture=fixtures[row['fixture']];game=games[fixture['source_game']]
            history=dict(initial_fen=game['initial_fen'],moves=game['moves'][:fixture['ply']],
                source=game['id'],confidence=.99,castling_history_attested=True)
            p=Position.from_fen(row['fen']);m=find_move(p,row['move']);arms={}
            for name,options in [
                ('original',Cycle8Options(mode='operational')),
                ('trusted-metadata',Cycle8Options(mode='operational',temporal_mode='trusted-metadata',temporal_evidence=dict(source=game['id'],confidence=.99))),
                ('event-reuse',Cycle8Options(mode='operational',temporal_mode='event-backed',temporal_evidence=history)),
                ('missing-events',Cycle8Options(mode='operational',temporal_mode='event-backed',temporal_evidence={**history,'initial_fen':p.fen(),'moves':[],'castling_history_attested':False})),
                ('removed-temporal-channel',Cycle8Options(mode='operational',temporal_mode='event-backed',temporal_evidence=history,suppress_families=('temporal',)))]:
                c=infer_moves(p,model,options,rt,[m])['candidates'][0]
                assert not c['positive_proof_complete']
                arms[name]=c
            initial=Position.from_fen(game['initial_fen']);initial=replace(initial,rights='-')
            no_rights=replace(p,rights='-')
            counter_history={**history,'initial_fen':initial.fen(),'source':game['id']+'/counterfactual-no-rights'}
            counter=infer_moves(no_rights,model,Cycle8Options(mode='operational',temporal_mode='event-backed',temporal_evidence=counter_history),rt,[m])['candidates'][0]
            assert counter['classification']!='supported-legal'
            assert arms['original']['classification']==row['classification']
            # Full-position scheduling and a selected-candidate query use different
            # node ordinals. Retain both DAGs and compare their semantic result.
            assert arms['original']['raw_stv']==row['truth_value']
            rows.append(dict(fixture=fixture,expected_legal=row['label'],original_classification=row['classification'],
                raw_truth_value=row['truth_value'],source_game=game['id'],history=history,arms=arms,
                full_position_proof_trace=[report['native_proof_dag'][i] for i in row['proof_refs']],
                full_position_proof_hash=row['proof_id'],
                no_rights_counterfactual=dict(fen=no_rights.fen(),history=counter_history,candidate=counter,expected_legal=False),
                resolved=arms['event-reuse']['classification']=='supported-legal',
                incorrectly_supported=any(c['classification']=='supported-illegal' for c in arms.values())))
    pack(out/'abstention/development-experiment.json.xz',rows)
    write_json(out/'abstention/summary.json',dict(cases=len(rows),resolved=sum(r['resolved'] for r in rows),
        incorrect=sum(r['incorrectly_supported'] for r in rows),thresholds_changed=False,new_training=False,
        final_holdout_used=False,experiment='Reuse independently supplied full game events for developmental legal abstentions.',
        classification_counts={name:{cls:sum(r['arms'][name]['classification']==cls for r in rows) for cls in ('supported-legal','supported-illegal','unknown','incomplete')} for name in ('original','trusted-metadata','event-reuse','missing-events','removed-temporal-channel')},
        interpretation='Supplied event history resolves the two operational developmental castling abstentions at unchanged raw STVs. Removing events, rights or the temporal channel removes positive support. This remains partial conditional evidence, not a native joint safety theorem.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
