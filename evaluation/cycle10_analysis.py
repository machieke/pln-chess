"""Offline external metrics, complete failure census and game-cluster calibration."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from evaluation.cycle9_analysis import metrics,fit,probability_metrics,cluster_intervals,selective,bin_index
from scripts.cycle9_baseline import sha

TAXONOMY=('movement-geometry','ray-obstruction','destination-occupancy','friendly-piece-interaction','capture-eligibility',
          'king-exposure','pins','discovered-attacks','double-check','check-resolution','promotion','castling','en-passant',
          'historical-uncertainty','insufficient-evidence','overly-specific-relational-abstraction','native-PLN-inference-limitation',
          'candidate-generation-limitation','timeout-or-inference-budget')
FIELDS=('fixture','family','source_game','dependence_group','move','piece','label','classification','legacy_classification',
        'truth_value','local_truth_value','proof_status','status','mode','self_check','tags','destination_exists','root_cause',
        'abstention_reason','model_version','runtime_version','promotion','unknown_squares')


def categories(row,fixture):
    text=' '.join(row['abstention_reason'])+' '+str(row['root_cause']);result=[]
    if row['classification']=='incomplete':result.append('timeout-or-inference-budget')
    if 'history' in text.lower() or 'histor' in text.lower() or 'Previous double push' in text:
        result.append('historical-uncertainty')
    if 'en-passant' in text:result.append('en-passant')
    if 'castl' in text.lower():result.append('castling')
    if row['promotion']:result.append('promotion')
    if 'geometry' in text or 'movement-prior' in text:result.append('movement-geometry')
    if 'obstruct' in text:result.append('ray-obstruction')
    if 'friendly' in text:result.append('friendly-piece-interaction')
    if 'destination' in text:result.append('destination-occupancy')
    if 'capture' in text:result.append('capture-eligibility')
    if row['self_check']:result.append('king-exposure')
    if fixture.get('pinned_pieces'):result.append('pins')
    if fixture.get('discovered_check_opportunities'):result.append('discovered-attacks')
    if fixture.get('double_check'):result.append('double-check')
    if fixture.get('in_check'):result.append('check-resolution')
    # Position contexts (for example pins) must not hide an explicitly missing
    # local hypothesis. Keep availability distinct from historical provenance.
    missing_local='No matching pooled local hypothesis.' in text or row['root_cause']=='missing-movement-prior'
    if missing_local:
        result.extend(('insufficient-evidence','overly-specific-relational-abstraction'))
    if not result:
        tv=row['local_truth_value']
        result.append('insufficient-evidence' if not tv or tv['confidence']<.25 else 'native-PLN-inference-limitation')
        if 'missing' in text:result.append('overly-specific-relational-abstraction')
    return list(dict.fromkeys(result))


def collect(out,arm='frozen'):
    data=read_json(out/'datasets/dataset.json');fixtures={f['id']:f for f in data['positions']}
    rows=[];positions=[];failures=[];receipts={}
    for path in sorted((out/'evaluation').glob(arm+'-operational-*.receipt.json')):
        receipt=read_json(path);report=read_gzip(out/receipt['artifact']);receipts[receipt['artifact']]=receipt['sha256']
        positions.extend({**p,'source_collection':fixtures[p['fixture']]['source_collection'],'split':report['split']} for p in report['positions'])
        for row in report['rows']:
            fixture=fixtures[row['fixture']]
            compact={k:row[k] for k in FIELDS};compact.update(split=report['split'],source_collection=fixture['source_collection'])
            rows.append(compact)
            failure=(row['label'] and row['classification']!='supported-legal') or (not row['label'] and row['classification']=='supported-legal')
            if failure:
                proof=[report['native_proof_dag'][i] for i in row['proof_refs']];assert digest(proof)==row['proof_id']
                failures.append(dict(index=len(failures),fixture=fixture,row=row,native_proof_trace=proof,
                    categories=categories(row,fixture),kind='abstention' if row['classification'] in ('unknown','incomplete') else 'error',
                    affected_hypotheses=row['rule_ids'],supporting_evidence=row['evidence_ids'],dependence_groups=row['dependence_groups'],
                    assessment='Missing supplied history is distinct from missing movement knowledge.' if 'historical-uncertainty' in categories(row,fixture) else 'Taxonomy is structural triage; causal attribution requires the recorded interventions, not a category label alone.'))
        for p in report['positions']:
            missing=fixtures[p['fixture']].get('candidate_generation_missing',[])
            if missing:failures.append(dict(index=len(failures),fixture=fixtures[p['fixture']],missing_candidates=missing,
                categories=['candidate-generation-limitation'],kind='candidate-generation-error',native_proof_trace=[]))
    return data,rows,positions,failures,receipts


def summarize(out,arm='frozen'):
    out=Path(out);data,rows,positions,failures,receipts=collect(out,arm);fixtures={f['id']:f for f in data['positions']}
    summary={}
    def group(name,selected,ps):
        summary[name]=dict(complete=metrics(selected,ps),in_board=metrics([r for r in selected if r['destination_exists']],ps),
            intervals=cluster_intervals(selected,ps,draws=400),per_piece={p:metrics([r for r in selected if r['piece']==p],[]) for p in sorted({r['piece'] for r in selected})},
            special_moves={kind:metrics([r for r in selected if kind in r['tags'] or (kind=='promotion' and r['promotion'])],[]) for kind in ('castling','en-passant','promotion')})
        summary[name]['intervals']['method']='Percentile source-game / controlled-pair bootstrap; 400 draws. Opening-family and player correlation may remain.'
    for split in sorted({r['split'] for r in rows}):
        selected=[r for r in rows if r['split']==split];ps=[p for p in positions if p['split']==split];group(split,selected,ps)
        for source in sorted({r['source_collection'] for r in selected}):
            group(split+'/'+source,[r for r in selected if r['source_collection']==source],[p for p in ps if p['source_collection']==source])
    factors={}
    factor_functions={'phase':lambda f:f.get('phase','unknown'),'material':lambda f:str((f.get('material_count',0)//8)*8)+'-'+str((f.get('material_count',0)//8)*8+7),
        'opening_family':lambda f:f.get('opening_family','unknown'),'tactical_density':lambda f:'high' if f.get('tactical_density',0)>=.5 else 'low',
        'legal_moves':lambda f:str((f.get('legal_move_count',0)//10)*10),'attacked_pieces':lambda f:str(f.get('attacked_pieces',0)),
        'multiple_attackers':lambda f:str(f.get('multiple_attacked_pieces',0)),'history':lambda f:f.get('history_completeness','unknown')}
    testrows=[r for r in rows if r['split']=='external-test'];testpos=[p for p in positions if p['split']=='external-test']
    for factor,fn in factor_functions.items():
        by=defaultdict(list);bypos=defaultdict(list)
        for row in testrows:by[fn(fixtures[row['fixture']])].append(row)
        for pos in testpos:bypos[fn(fixtures[pos['fixture']])].append(pos)
        factors[factor]={key:metrics(values,bypos[key]) for key,values in sorted(by.items())}
    census={cat:dict(positions=len({r['fixture']['id'] for r in failures if cat in r['categories']}),
        candidates=sum(cat in r['categories'] for r in failures),
        errors=sum(cat in r['categories'] and r['kind']!='abstention' for r in failures),
        abstentions=sum(cat in r['categories'] and r['kind']=='abstention' for r in failures),
        representative_proof_indices=[r['index'] for r in failures if cat in r['categories']][:5]) for cat in TAXONOMY}
    nonexact={p['fixture'] for p in positions if not p['exact']};accounted={r['fixture']['id'] for r in failures}
    assert nonexact<=accounted,(arm,nonexact-accounted)
    write_json(out/f'analysis/{arm}-summary.json',summary);write_json(out/f'analysis/{arm}-factors.json',factors)
    write_json(out/f'analysis/{arm}-failure-index.json',dict(nonexact_positions=len(nonexact),unresolved_candidates=len(failures),
        all_nonexact_positions_accounted_for=True,categories=census,entries=[dict(index=f['index'],fixture=f['fixture']['id'],
        move=f.get('row',{}).get('move'),kind=f['kind'],categories=f['categories']) for f in failures]))
    pack(out/f'analysis/{arm}-failure-proofs.json.xz',failures)
    pack(out/f'analysis/{arm}-rows.json.xz',dict(rows=rows,positions=positions))
    write_json(out/f'analysis/{arm}-verification.json',dict(passed=True,rows=len(rows),positions=len(positions),
        all_positions_accounted_for=True,nonexact_positions=len(nonexact),failure_candidates=len(failures),receipts=receipts,
        dataset_hash=data['hash'],model_versions=sorted({r['model_version'] for r in rows})))
    if arm=='frozen':
        secondary={};matched=set()
        for mode in ('strict','experimental'):
            rs=[];ps=[]
            for path in sorted((out/'evaluation').glob('frozen-'+mode+'-*.receipt.json')):
                receipt=read_json(path);report=read_gzip(out/receipt['artifact'])
                rs.extend(report['rows']);ps.extend(report['positions']);matched.update(p['fixture'] for p in report['positions'])
            assert len(ps)==30
            secondary[mode]=dict(complete=metrics(rs,ps),in_board=metrics([r for r in rs if r['destination_exists']],ps),
                proof_status_counts=dict(Counter(r['proof_status'] for r in rs)),
                complete_positive_proofs=sum(r['positive_proof_complete'] for r in rs))
        rs=[r for r in rows if r['fixture'] in matched];ps=[p for p in positions if p['fixture'] in matched]
        secondary['matched-operational']=dict(complete=metrics(rs,ps),in_board=metrics([r for r in rs if r['destination_exists']],ps),
            proof_status_counts=dict(Counter(r['proof_status'] for r in rs)))
        write_json(out/'analysis/secondary-modes.json',dict(models=secondary,positions=30,source_games=len({p['source_game'] for p in ps}),
            selection='Registered first ten final-test positions per collection; secondary mode comparison, not a second representative external sample.',
            scope='Strict and experimental modes retain the incomplete positive composition boundary; unknown positives do not imply movement-ontology errors.'))
    return data,rows,positions


def frozen_calibration(out):
    """Finish and record the original C9 calibration test before any new fit."""
    out=Path(out);data=read_json(out/'datasets/dataset.json')
    path=ROOT/'artifacts/cycle9/calibration/results.json';original=read_json(path)
    assert sha(path)==read_json(ROOT/'artifacts/cycle9/acceptance.json')['calibration_sha256']
    rows=[];positions=0
    for receipt in sorted((out/'evaluation').glob('frozen-operational-*.receipt.json')):
        r=read_json(receipt);assert sha(out/r['artifact'])==r['sha256']
        report=read_gzip(out/r['artifact']);assert report['model_version']==original['model_version']
        positions+=len(report['positions'])
        rows.extend(dict(label=x['label'],truth_value=x['truth_value'],destination_exists=x['destination_exists'],split=report['split']) for x in report['rows'])
    assert positions==len(data['positions'])
    measurements={}
    for population in ('complete','in-board'):
        score=lambda r:original['mappings'][population][bin_index(r['truth_value']['strength'])]['probability']
        for split in data['counts']:
            selected=[r for r in rows if r['split']==split and (population=='complete' or r['destination_exists'])]
            measurements[population+'/'+split]=probability_metrics(selected,score)
    write_json(out/'calibration/frozen-evaluation.json',dict(passed=True,calibration_refit=False,completed_unix=time.time(),
        model_version=original['model_version'],original_calibration_sha256=sha(path),dataset_hash=data['hash'],
        positions=positions,rows=len(rows),measurements=measurements,scope='Unchanged Cycle 9 diagnostic map evaluated before fitting external calibration or training adaptation models.'))


def calibration(out):
    out=Path(out);assert read_json(out/'frozen-complete.json')['passed']
    assert sha(out/'calibration/frozen-evaluation.json')==read_json(out/'frozen-complete.json')['frozen_calibration_sha256']
    stored=read_gzip(out/'analysis/frozen-rows.json.xz');rows=stored['rows'];positions=stored['positions']
    old=read_json(ROOT/'artifacts/cycle9/calibration/results.json');cfg=read_json(ROOT/'configs/cycle10.json')
    calibration_rows=[r for r in rows if r['split']=='external-calibration'];mappings={};results={}
    original=defaultdict(list)
    for split in ('independent-games','adversarial','special-moves'):
        for path in sorted((out/'baseline/evaluation').glob('operational-'+split+'-*.json.xz')):
            original['Cycle9-reproduced/'+split].extend({k:r[k] for k in FIELDS} for r in read_gzip(path)['rows'])
    for population in ('complete','in-board'):
        keep=lambda r:population=='complete' or r['destination_exists']
        fitrows=[r for r in calibration_rows if keep(r)];mapping=fit(fitrows);mappings[population]=mapping
        groups={split:[r for r in rows if r['split']==split and keep(r)] for split in sorted({r['split'] for r in rows})}
        for source in sorted({r['source_collection'] for r in rows if r['split']=='external-test'}):
            groups['external-test/'+source]=[r for r in rows if r['split']=='external-test' and r['source_collection']==source and keep(r)]
        groups['external-history-sensitive-FEN-only']=[r for r in rows if r['split']=='external-test' and keep(r) and any('castl' in t or 'en-passant' in t for t in r['tags'])]
        groups.update({name:[r for r in subset if keep(r)] for name,subset in original.items()})
        for name,selected in groups.items():
            ids={r['fixture'] for r in selected};ps=[p for p in positions if p['fixture'] in ids]
            scores={'raw-strength':lambda r:r['truth_value']['strength'],
                    'frozen-C9':lambda r:old['mappings'][population][bin_index(r['truth_value']['strength'])]['probability'],
                    'external-validation-fit':lambda r:mapping[bin_index(r['truth_value']['strength'])]['probability']}
            measurements={key:dict(**probability_metrics(selected,score),
                cluster_interval=cluster_intervals(selected,ps,score,draws=cfg['bootstrap_replicates'])) for key,score in scores.items()}
            for measurement in measurements.values():
                measurement['cluster_interval']['method']='Percentile source-game / controlled-pair bootstrap; four hundred draws, residual opening/player dependence remains.'
            confidence_bins=[]
            for index in range(10):
                subset=[r for r in selected if bin_index(r['truth_value']['confidence'])==index]
                if subset:confidence_bins.append(dict(bin=index,n=len(subset),mean_native_confidence=sum(r['truth_value']['confidence'] for r in subset)/len(subset),
                    legal_frequency=sum(r['label'] for r in subset)/len(subset),scope='Association diagnostic; confidence is not a legality probability.'))
            results[population+'/'+name]=dict(measurements=measurements,confidence_bins=confidence_bins,selective=selective(selected))
    write_json(out/'calibration/results.json',dict(schema=10,diagnostic_only=True,changes_classification=False,fitted_unix=time.time(),
        model_version=old['model_version'],frozen_mapping=old['mappings'],external_mapping=mappings,
        fit_split='external-calibration',fit_games=len({r['source_game'] for r in calibration_rows}),fit_positions=len({r['fixture'] for r in calibration_rows}),
        dataset_hash=read_json(out/'datasets/dataset.json')['hash'],frozen_calibration_hash=digest(old),results=results,
        historical_comparison=old.get('evaluations',{}),
        limits=['Candidate and position observations are clustered by game/pair. Repeated openings, engines and players can add residual dependence.',
                'Calibration fitting occurs only after frozen evaluation. Final-test labels never choose bins, thresholds, hypotheses or operational promotion.',
                'Zero-error bootstraps are not universal zero-risk claims. The external diagnostic mapping does not alter native inference.']))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--arm',default='frozen');p.add_argument('--calibration',action='store_true')
    a=p.parse_args();summarize(a.out,a.arm)
    if a.calibration:calibration(a.out)
