"""Offline empirical diagnostics; never imported by native inference."""
import argparse
from collections import Counter,defaultdict
from functools import lru_cache
import csv
import math
from pathlib import Path
import random
import chess
from pln_chess.common import read_json,write_json,digest
from pln_chess.domain import Position,inside
from pln_chess.hypotheses import candidates
from pln_chess.spatial import geometry,ray_cells
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from evaluation.experiments import summarize


def wilson(success,n):
    if not n:return None
    z=1.959963984540054;p=success/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,center-half),min(1,center+half)]


def bin_index(value):return min(9,max(0,int(value*10)))


def probability_metrics(rows,score):
    if not rows:return dict(n=0,brier=None,log_loss=None,ece=None,bins=[])
    bins=defaultdict(list);brier=loss=0
    for r in rows:
        p=score(r);y=int(r['label']);assert 0<=p<=1
        brier+=(p-y)**2;q=min(1-1e-12,max(1e-12,p));loss-=y*math.log(q)+(1-y)*math.log1p(-q)
        bins[bin_index(p)].append((p,y))
    result=[];ece=0
    for b,values in sorted(bins.items()):
        n=len(values);pred=sum(p for p,_ in values)/n;success=sum(y for _,y in values);actual=success/n
        ece+=n*abs(pred-actual)
        result.append(dict(bin=b,n=n,mean_score=pred,observed_legal_frequency=actual,
            interval95_naive_wilson=wilson(success,n)))
    return dict(n=len(rows),brier=brier/len(rows),log_loss=loss/len(rows),ece=ece/len(rows),bins=result,
        log_loss_clipping=1e-12,interval_scope='Bin Wilson intervals ignore dependence; use game-cluster intervals for overall metrics.')


def fit(rows):
    bins=[dict(n=0,legal=0) for _ in range(10)]
    for r in rows:
        b=bins[bin_index(r['truth_value']['strength'])];b['n']+=1;b['legal']+=int(r['label'])
    return [dict(**b,probability=(b['legal']+1)/(b['n']+2),bin=i) for i,b in enumerate(bins)]


def metrics(rows,positions):
    result=summarize([{**r,'classification':r['legacy_classification']} for r in rows],positions)
    result.update(false_illegal=sum(r['label'] and r['classification']=='supported-illegal' for r in rows),
        unknown=sum(r['classification']=='unknown' for r in rows),incomplete=sum(r['classification']=='incomplete' for r in rows),
        n=len(rows),positions=len(positions),exact_positions=sum(p['exact'] for p in positions))
    return result


def cluster_intervals(rows,positions,probability=None,draws=500):
    """Aggregate sufficient statistics by source game/pair, then resample clusters."""
    groups=defaultdict(lambda:[0]*9)
    for r in rows:
        g=groups[r['source_game'] or r['dependence_group']];positive=r['classification']=='supported-legal'
        g[0]+=1;g[1]+=int(r['label']);g[2]+=int(positive and r['label']);g[3]+=int(positive)
        g[4]+=int(r['classification'] in ('supported-legal','supported-illegal'))
        g[5]+=int((positive and not r['label']) or (r['classification']=='supported-illegal' and r['label']))
        if probability:g[8]+=(probability(r)-r['label'])**2
    for p in positions:
        g=groups[p['source_game'] or p['dependence_group']];g[6]+=1;g[7]+=int(p['exact'])
    values=list(groups.values());rng=random.Random(90991);samples=defaultdict(list)
    if not values:return dict(clusters=0,interval95={})
    for _ in range(draws):
        total=[0]*9
        for __ in values:
            g=rng.choice(values)
            for i,v in enumerate(g):total[i]+=v
        for name,num,den in [('recall',total[2],total[1]),('precision',total[2],total[3]),
            ('coverage',total[4],total[0]),('exact_move_set_accuracy',total[7],total[6]),
            ('selective_risk',total[5],total[4]),('calibrated_brier',total[8],total[0])]:
            if den and (name!='calibrated_brier' or probability):samples[name].append(num/den)
    return dict(clusters=len(values),draws=draws,method='Percentile source-game / controlled-pair bootstrap; synthetic sampling only.',
        interval95={k:[sorted(v)[int(.025*len(v))],sorted(v)[min(len(v)-1,int(.975*len(v)))]] for k,v in samples.items()},
        warning='Zero observed errors produce a degenerate bootstrap interval, not a universal zero-risk guarantee. Games in an opening family may remain correlated.')


def selective(rows):
    result=[]
    for threshold in (0,.1,.25,.5,.7,.8,.9,.95,.99):
        selected=[r for r in rows if r['classification'] in ('supported-legal','supported-illegal') and r['truth_value']['confidence']>=threshold]
        errors=sum((r['classification']=='supported-legal')!=r['label'] for r in selected)
        result.append(dict(min_native_confidence=threshold,n=len(selected),errors=errors,
            coverage=len(selected)/len(rows) if rows else 0,risk=errors/len(selected) if selected else None,
            error_interval95_naive_wilson=wilson(errors,len(selected)),metrics=metrics(selected,[])))
    return result


def cause(row):
    if row['classification']=='incomplete':return 'candidate-generation-or-budget'
    if row['mode']!='operational' and row['label']:return 'native-inference-limitation'
    if row['unknown_squares']:return 'missing-supporting-evidence'
    text=' '.join(row['abstention_reason'])
    if 'history' in text or 'temporal' in text or row['root_cause'] in ('en-passant-history','castling-history-transit'):return 'incomplete-history'
    if 'dependency' in text or 'overlap' in text:return 'evidence-dependence'
    if row['root_cause'] in ('missing-movement-prior','geometry-abstraction-mismatch'):return 'missing-learned-hypothesis'
    if row['local_truth_value'] and (row['local_truth_value']['confidence']<.25 or .2<row['local_truth_value']['strength']<.8):return 'classification-threshold-or-low-evidence'
    return 'native-inference-limitation-or-specific-abstraction'


@lru_cache(maxsize=1024)
def board_context(fen):
    p=Position.from_fen(fen);b=chess.Board(fen)
    return p,b,{m.notation:m for m in candidates(p)}


def feature_groups(row):
    p,b,moves=board_context(row['fen']);m=moves[row['move']];mover=p.at(m.start);destination=p.at(m.end)
    occupancy=lambda piece:'empty' if piece is None else 'friendly' if piece.owner==mover.owner else 'opponent'
    ray=ray_cells(m.start,m.end);cells=[occupancy(p.at(s)) if inside(s) else 'boundary' for s in ray]
    checks=len(b.checkers());start=chess.square(*m.start)
    return dict(piece=row['piece'],movement_geometry=geometry(m.start,m.end,p.turn)['family'],ray_length=str(len(ray)),
        intermediate_occupancy='/'.join(sorted(set(cells))) or 'no-intermediate-cells',
        destination_occupancy=occupancy(destination) if inside(m.end) else 'boundary',
        capture_type='en-passant' if m.effect=='en-passant' else 'opponent' if destination and destination.owner!=mover.owner else 'non-capture',
        king_exposure=str(row['self_check']),pin_configuration=str(b.is_pinned(b.turn,start)),double_check=str(checks>1),
        check_resolution='resolves' if checks and row['label'] else 'unresolved' if checks else 'not-in-check',
        promotion=m.promotion or 'none',castling=str(m.effect=='castle'),en_passant=str(m.effect=='en-passant'),
        missing_history=str(m.effect in ('castle','en-passant')),unknown_sensory=str(bool(row['unknown_squares'])))


def structural_metrics(rows):
    counts=defaultdict(Counter)
    for r in rows:
        for feature,value in feature_groups(r).items():
            c=counts[feature+'/'+value];c['candidates']+=1;c['legal']+=int(r['label']);c[r['classification']]+=1
            c['true_positive']+=int(r['label'] and r['classification']=='supported-legal')
            c['false_legal']+=int(not r['label'] and r['classification']=='supported-legal')
            c['false_illegal']+=int(r['label'] and r['classification']=='supported-illegal')
    return {k:{**c,'recall':c['true_positive']/c['legal'] if c['legal'] else None} for k,c in sorted(counts.items())}


def run(out):
    out=Path(out);data=read_json(out/'datasets/dataset.json');by=defaultdict(lambda:dict(rows=[],positions=[]));representatives={}
    receipts=[];proof_count=0
    for path in sorted((out/'evaluation').glob('*.receipt.json')):
        receipt=read_json(path);report=read_gzip(out/receipt['artifact']);receipts.append(receipt)
        key=(report['mode'],report['split']);by[key]['positions'].extend(report['positions'])
        for r in report['rows']:
            proof=[report['native_proof_dag'][i] for i in r['proof_refs']]
            assert digest(proof)==r['proof_id'];proof_count+=1
            unresolved=r['classification'] in ('unknown','incomplete') or (r['classification']=='supported-legal')!=r['label'] and r['classification']!='supported-illegal' or (r['classification']=='supported-illegal' and r['label'])
            if unresolved:
                key2=(report['mode'],cause(r),r['root_cause'])
                representatives.setdefault(key2,dict(row=r,proof_trace=proof,artifact=receipt['artifact'],cause=cause(r)))
            keep=('fixture','family','source_game','dependence_group','fen','move','piece','label','classification','legacy_classification','mode',
                  'truth_value','local_truth_value','self_check','tags','destination_exists','root_cause','proof_id','rule_ids','evidence_ids',
                  'dependence_groups','abstention_reason','unknown_squares','promotion','backoff')
            by[key]['rows'].append({k:r[k] for k in keep})
    summary={};calibration_rows=by[('operational','calibration')]['rows'];assert len(by[('operational','calibration')]['positions'])==100
    mappings={population:fit([r for r in calibration_rows if population=='complete' or r['destination_exists']]) for population in ('complete','in-board')}
    calibration=dict(schema='empirical-calibration-v9',native=False,model_version=receipts[0]['identity']['model_version'],dataset_hash=data['hash'],
        fit_split='calibration',fit_games=20,fit_positions=100,fit_rows=len(calibration_rows),mappings=mappings,
        score='Ten strength bins; Laplace (legal+1)/(n+2), independent per complete/in-board population.',
        scope='Diagnostic estimate of legal-move frequency in synthetic cohorts. Does not change native STVs, classification, or proof status.',evaluations={})
    comparisons={}
    for (mode,split),item in by.items():
        rows=item['rows'];positions=item['positions'];key=f'{mode}/{split}'
        expected=data['counts'][split] if mode=='operational' or split=='special-moves' else 25
        assert len(positions)==expected,(key,len(positions),expected)
        summary[key]=dict(complete=metrics(rows,positions),in_board=metrics([r for r in rows if r['destination_exists']],positions),
            uncertainty=cluster_intervals(rows,positions),per_piece={piece:metrics([r for r in rows if r['piece']==piece],[]) for piece in sorted({r['piece'] for r in rows})},
            failure_families=dict(Counter(r['root_cause'] for r in rows if r['classification']=='unknown')),
            causes=dict(Counter(cause(r) for r in rows if r['classification']=='unknown')),
            structural_groups=structural_metrics(rows),
            per_family={family:metrics([r for r in rows if r['family']==family],[p for p in positions if p['family']==family]) for family in sorted({r['family'] for r in rows})})
        if mode!='operational' or split in ('development','calibration'):continue
        cal={}
        for population in ('complete','in-board'):
            selected=[r for r in rows if population=='complete' or r['destination_exists']]
            mapping=mappings[population]
            scores={'raw-strength':lambda r:r['truth_value']['strength'],
                    'raw-confidence-as-diagnostic-score':lambda r:r['truth_value']['confidence'],
                    'strength-confidence-diagnostic':lambda r:.5+(r['truth_value']['strength']-.5)*r['truth_value']['confidence'],
                    'empirical-calibrated':lambda r:mapping[bin_index(r['truth_value']['strength'])]['probability']}
            cal[population]={name:probability_metrics(selected,score) for name,score in scores.items()}
            calibrated=scores['empirical-calibrated']
            cal[population]['cluster_uncertainty']=cluster_intervals(selected,positions,calibrated)
            cal[population]['selective_risk_coverage']=selective(selected)
            strata={**{'piece/'+p:[r for r in selected if r['piece']==p] for p in sorted({r['piece'] for r in selected})},
                **{'special/'+t:[r for r in selected if t in r['tags']] for t in ('promotion','castling','en-passant')},
                **{'evidence-groups/'+str(n):[r for r in selected if min(20,len(r['dependence_groups']))==n] for n in sorted({min(20,len(r['dependence_groups'])) for r in selected})}}
            cal[population]['strata']={k:dict(native=probability_metrics(v,scores['raw-strength']),calibrated=probability_metrics(v,calibrated),selective=selective(v)) for k,v in strata.items()}
        calibration['evaluations'][split]=cal
    adversarial={r['fixture']:{} for r in by[('operational','adversarial')]['rows']}
    for r in by[('operational','adversarial')]['rows']:adversarial[r['fixture']][r['move']]=r
    pair_results=[]
    for pair in data['counterfactual_pairs']:
        rows=[adversarial[f][pair['focus_move']] for f in pair['fixtures']]
        pair_results.append(dict(**pair,results=rows,correct_supported=[r['classification']==('supported-legal' if r['label'] else 'supported-illegal') for r in rows],
            safe=all(not ((r['classification']=='supported-legal' and not r['label']) or (r['classification']=='supported-illegal' and r['label'])) for r in rows)))
    write_json(out/'analysis/evaluation-summary.json',summary)
    write_json(out/'calibration/results.json',calibration)
    pack(out/'analysis/failure-proofs.json.xz',list(representatives.values()))
    write_json(out/'analysis/failure-index.json',[dict(index=i,cause=r['cause'],mode=r['row']['mode'],family=r['row']['root_cause'],
        fixture=r['row']['fixture'],move=r['row']['move'],classification=r['row']['classification'],expected_legal=r['row']['label'],
        proof_hash=r['row']['proof_id'],artifact=r['artifact'],rule_ids=r['row']['rule_ids'],evidence_ids=r['row']['evidence_ids'])
        for i,r in enumerate(representatives.values())])
    pack(out/'analysis/adversarial-pairs.json.xz',pair_results)
    write_json(out/'analysis/verification.json',dict(proof_records_reconstructed=proof_count,representative_families=len(representatives),
        shards=len(receipts),dataset_hash=data['hash'],all_positions_accounted_for=True,
        pair_count=len(pair_results),safe_pairs=sum(r['safe'] for r in pair_results),fully_supported_pairs=sum(all(r['correct_supported']) for r in pair_results)))
    path=out/'calibration/predictions.csv';path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as stream:
        writer=csv.writer(stream);writer.writerow(['split','fixture','source_game','move','piece','in_board','label','classification','native_strength','native_confidence','calibrated_in_board','proof_id'])
        for (mode,split),item in sorted(by.items()):
            if mode!='operational':continue
            for r in item['rows']:
                writer.writerow([split,r['fixture'],r['source_game'],r['move'],r['piece'],r['destination_exists'],r['label'],r['classification'],r['truth_value']['strength'],r['truth_value']['confidence'],
                    mappings['in-board'][bin_index(r['truth_value']['strength'])]['probability'] if r['destination_exists'] else '',r['proof_id']])
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
