"""Complete label revisions, including unresolved and missing endpoints."""
from collections import Counter
from pathlib import Path
from pln_chess.common import ROOT,read_json
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out='artifacts/cycle14'):
    out=Path(out);panels={}
    for kind,oldname in (('immediate','reference-labels.json'),('temporal','temporal-labels.json')):
        old=read_json(ROOT/'artifacts/cycle13/datasets'/oldname)['records']
        data=read_json(out/f'labels/{kind}-g1/index.json');latest={r['id']:r for r in data['records']}
        revisions=[]
        for previous in old:
            current=latest[previous['id']]
            assert current['supersedes']==previous['evidence_id']
            revisions.append(dict(id=previous['id'],original_label=previous['label'],new_label=current['label'],
                original_evidence_id=previous['evidence_id'],superseding_evidence_id=current['evidence_id'],
                reason=current['reason'],horizon=current['horizon'],split=current['split'],
                raw_reference=data['raw_manifest'][current['id']],
                original_actor=current['original_actor'],unknown_is_not_negative_evidence=True))
        unknown=[r for r in revisions if r['original_label']=='unknown']
        historical_test=[r for r in unknown if r['split']=='historical-test']
        panels[kind]=dict(N_registered=len(latest),counts=data['counts'],causes=dict(Counter(r['reason'] for r in latest.values())),
            actual_reported_nodes=data['actual_reported_nodes'],historical_revisions=revisions,
            old_unknown_N=len(unknown),old_unknown_new_counts=dict(Counter(r['new_label'] for r in unknown)),
            old_test_unknown_N=len(historical_test),old_test_unknown_new_counts=dict(Counter(r['new_label'] for r in historical_test)),
            old_unknown_causes=dict(Counter(r['reason'] for r in unknown)),
            strata=[dict(split=s,horizon=h,N=len(selected),counts=dict(Counter(r['label'] for r in selected)),
                causes=dict(Counter(r['reason'] for r in selected))) for s,h in sorted({(r['split'],r['horizon']) for r in latest.values()})
                for selected in [[r for r in latest.values() if r['split']==s and r['horizon']==h]]],
            index_sha256=sha(out/f'labels/{kind}-g1/index.json'))
    assert panels['immediate']['old_test_unknown_N']==41
    assert panels['temporal']['old_unknown_N']==50
    atomic_json(out/'reference-audit/resolution-census.json',dict(passed=True,panels=panels,
        generations_preserve_original=True,model_predictions_used=False,
        parser_finding='Synthetic aggregate-dict reuse can retain a stale bound flag; the 41 rerun historical immediate unknown pairs exhibited zero observed stale-bound pairs. This defect is not established as their empirical cause.',
        method_change='New independent candidate-restricted root searches and preregistered escalation differ from historical MultiPV. Changes are operational supervision revisions, not corrections proven against true chess value.',
        temporal_missing='A missing selected PV or short supplied line is an unavailable endpoint. It remains unknown; no success-based branch replacement.',
        native_inference_or_calibrated_probability_claim=False))


if __name__=='__main__':run()
