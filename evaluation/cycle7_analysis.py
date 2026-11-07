"""Paired game-cluster deltas, abstention taxonomy and auditable proof examples."""
from collections import Counter, defaultdict
from pathlib import Path
import random
from pln_chess.common import read_json, write_json, digest
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack

def paired(before,after):
    assert before['dataset_hash']==after['dataset_hash']
    a={p['fixture']:p for p in before['positions']};b={p['fixture']:p for p in after['positions']};assert a.keys()==b.keys()
    assert [(r['fixture'],r['move'],r['label']) for r in before['rows']]==[(r['fixture'],r['move'],r['label']) for r in after['rows']]
    deltas=[];clusters=defaultdict(list)
    for fid,p in a.items():
        q=b[fid];expected=set(p['expected']);assert expected==set(q['expected'])
        row={'fixture':fid,'game':p.get('source_game'),'family':p['family'],'legal_candidates':len(expected),
            'before_exact':p['exact'],'after_exact':q['exact'],'added_predictions':sorted(set(q['predicted'])-set(p['predicted'])),
            'removed_predictions':sorted(set(p['predicted'])-set(q['predicted'])),
            'before_tp':len(expected&set(p['predicted'])),'after_tp':len(expected&set(q['predicted']))}
        deltas.append(row);clusters[p.get('source_game') or fid].append(row)
    rng=random.Random(707);keys=sorted(clusters);samples=[]
    for _ in range(1000):
        rows=[r for k in rng.choices(keys,k=len(keys)) for r in clusters[k]];total=sum(r['legal_candidates'] for r in rows)
        samples.append((sum(r['after_tp']-r['before_tp'] for r in rows)/total if total else 0,
            sum(int(r['after_exact'])-int(r['before_exact']) for r in rows)/len(rows)))
    def ci(index):
        values=sorted(s[index] for s in samples);return [values[25],values[974]]
    return {'positions':deltas,'cluster_count':len(keys),'bootstrap_replicates':1000,'seed':707,
        'bootstrap_unit':'source game; standalone fixtures use fixture ID','recall_delta_95_percentile_interval':ci(0),
        'exact_set_delta_95_percentile_interval':ci(1),'small_sample_caution':len(keys)<20,
        'interpretation':'Paired empirical intervals for this generated corpus; no population-wide or external-game guarantee.'}

def unknown_categories(row):
    cause=row['root_cause'];reason=' '.join(row['abstention_reason']).lower();tags=row.get('tags',[]);categories=[]
    if any(s in cause for s in ('castl','history','en-passant')):categories.append('history')
    if 'destination' in cause:categories.append('occupancy')
    if 'obstruct' in cause or 'block' in cause:categories.append('obstruction')
    if row.get('self_check') or 'exposure' in cause:categories.append('attack/exposure')
    if 'no matching pooled' in reason:categories+=['unseen feature combination','missing evidence']
    elif 'geometry' in cause:categories.append('movement geometry')
    if row['truth_value']['confidence']<.25:categories.append('confidence')
    if not categories:categories.append('missing evidence')
    return sorted(set(categories))

def example(report,row):
    return {**row,'native_proof':[report['native_proof_dag'][i] for i in row['proof_refs']],
        'policy_decision':report['policy_decisions'][row['decision_ref']]}

def run(out):
    out=Path(out);curves={};examples=[];partitions={};regressions=[];pairs={}
    for split in ('cycle6-independent-games','cycle7-independent-games'):
        base=read_gzip(out/f'evaluation/C7-frozen-{split}.json.xz');curves[split]={}
        unknown=[r for r in base['rows'] if r['classification']=='unknown']
        counts=Counter(c for r in unknown for c in unknown_categories(r))
        partitions[split]={'unknown':len(unknown),'legal_unknown':sum(r['label'] for r in unknown),
            'multi_label_counts':dict(counts),'note':'Categories can overlap; legal-candidate abstentions are counted separately from easy negatives.',
            'rows':[{k:r[k] for k in ('fixture','move','piece','label','root_cause','truth_value','abstention_reason')}|{'categories':unknown_categories(r)} for r in unknown]}
        for budget in (0,2,4,8):
            name=f'C7-learned-{budget}';after=read_gzip(out/f'evaluation/{name}-{split}.json.xz')
            pair=paired(base,after);pairs[name+'-'+split]=pair
            curves[split][str(budget)]={'metrics':after['metrics'],'model_version':after['model_version'],
                'new_independent_games':budget,'new_selected_examples':budget*24,'paired':pair,
                'structural_family_metrics':after['metrics']['per_family'],'piece_metrics':after['metrics']['per_piece']}
        # Five useful successes and five legal abstentions, with actual evidence.
        for group,rows in [('success',[r for r in base['rows'] if r['label'] and r['classification']=='supported-legal'][:5]),
                           ('unresolved',[r for r in base['rows'] if r['label'] and r['classification']=='unknown'][:5])]:
            examples += [{'example_kind':group,'split':split,**example(base,r)} for r in rows]
    # Every label or proof regression, including intentionally destructive ablations.
    for summary in sorted((out/'evaluation').glob('*-summary.json')):
        name=summary.name.removesuffix('-summary.json')
        for split,entry in read_json(summary).items():
            target=out/'evaluation'/f'C7-frozen-{split}.json.xz'
            if not target.exists() or name=='C7-frozen':continue
            base=read_gzip(target);after=read_gzip(out/entry['artifact']);before={(r['fixture'],r['move']):r for r in base['rows']}
            delta=paired(base,after)
            write_json(out/f'paired/{name}-{split}.json',delta)
            for r in after['rows']:
                old=before[(r['fixture'],r['move'])]
                if (r['classification']=='supported-legal' and not r['label']) or (r['classification']=='supported-illegal' and r['label']) or (old['classification'] in ('supported-legal','supported-illegal') and r['classification']!=old['classification']):
                    regressions.append({'arm':name,'split':split,'before_classification':old['classification'],
                        'intentional_ablation':name.startswith('ablation-'),'intentional_mode_change':name in ('C7-strict','C7-experimental'),
                        'artifact':entry['artifact'],**{k:r[k] for k in ('fixture','fen','move','source_game','label','classification','truth_value','proof_status','proof_id','proof_refs','decision_ref','evidence_ids','dependence_groups','abstention_reason','root_cause','backoff')}})
    write_json(out/'learning-curves.json',curves);write_json(out/'unknown-analysis.json',partitions)
    pack(out/'proofs/representative-examples.json.xz',examples);pack(out/'proofs/all-regressions.json.xz',regressions)
    write_json(out/'regression-summary.json',{'count':len(regressions),'by_arm':dict(Counter(r['arm'] for r in regressions)),
        'by_root_cause':dict(Counter(r['root_cause'] for r in regressions)),
        'scope':'Includes expected strict abstentions and destructive ablations; default acceptance is evaluated separately.'})
    return curves

if __name__=='__main__':
    import sys
    run(sys.argv[1])
