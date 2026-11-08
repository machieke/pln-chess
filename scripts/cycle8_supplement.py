"""Offline cross-generation leakage audit and data/model file manifests."""
from pathlib import Path
from itertools import combinations
import argparse
import hashlib
from pln_chess.common import ROOT,read_json,write_json,digest
from training.cycle8_data import translation_key


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(out):
    out=Path(out);data=read_json(out/'datasets/dataset.json');parts={s:[p for p in data['positions'] if p['split']==s] for s in data['counts']}
    pairs=[]
    for a,b in combinations(sorted(parts),2):
        counts={}
        for field in ('symmetry_key','translation_key','structural_family','dependence_group','source_game'):
            x={p[field] for p in parts[a] if p.get(field) is not None};y={p[field] for p in parts[b] if p.get(field) is not None}
            counts[field]=len(x&y)
        assert not any(counts.values()),(a,b,counts)
        pairs.append({'partitions':[a,b],'overlap_counts':counts})
    paths=['fixtures/dataset.json','artifacts/cycle2/dataset.json','artifacts/cycle3/dataset.json','artifacts/cycle4/datasets/dataset.json','artifacts/cycle5/datasets/dataset.json','artifacts/cycle6/datasets/dataset.json','artifacts/cycle7/datasets/dataset.json']
    historical={translation_key(p['fen']) for path in paths for p in read_json(ROOT/path)['positions'] if p['split']=='train'}
    overlap={s:sum(p['translation_key'] in historical for p in rows) for s,rows in parts.items()}
    assert not any(overlap.values()),overlap
    audit={'passed':True,'dataset_hash':data['hash'],'producer_sha256':sha(__file__),'all_partition_pairs':pairs,'historical_training_translation_keys':len(historical),
        'historical_training_overlap':overlap,'historical_dataset_sha256':{p:sha(ROOT/p) for p in paths},
        'scope':'Complete-board translation/color/file-reflection equivalence and declared complete structural families. Reusable local subrelations intentionally recur; family names do not prove every added piece interacts causally.'}
    write_json(out/'datasets/cross-generation-audit.json',audit)
    write_json(out/'datasets/manifest.json',{'file':'datasets/dataset.json','sha256':sha(out/'datasets/dataset.json'),
        'content_hash':data['hash'],'registration_hash':data['registration_hash'],'seed':read_json(ROOT/'configs/cycle8.json')['seed'],
        'positions':data['counts'],'training_examples':len(data['examples']),'games':len(data['games']),
        'oracle':data['oracle'],'audit':'datasets/cross-generation-audit.json'})
    models={}
    for path in sorted((out/'model').glob('*.json')):
        if path.name=='manifest.json':continue
        model=read_json(path);copy=dict(model);version=copy.pop('version');assert digest(copy)==version
        groups=[]
        for h in model['hypotheses'].values():
            assert not {'fen','square','start','end','file','rank'}&set(h['descriptor'])
            groups.extend(h['dependence_groups'])
        models[path.stem]={'file':str(path.relative_to(out)),'sha256':sha(path),'bytes':path.stat().st_size,
            'version':version,'variant':model['variant'],'schema':model['schema'],'hypotheses':len(model['hypotheses']),
            'unique_source_groups':len(set(groups)),'training':model['training_report'],
            'runtime_version':model['source']['source']['source']['runtime_version']}
    write_json(out/'model/manifest.json',{'models':models,'scope':'Checkpoint file hashes and content versions; no native formulas are evaluated by this audit.'})
    base=read_json(out/'model/C8-promotion-relative.json')['hypotheses']
    repeated=read_json(out/'model/C8-no-dependence.json')['hypotheses'];effects=[]
    for identifier,h in base.items():
        other=repeated[identifier]
        effects.append({'hypothesis_id':identifier,'descriptor':h['descriptor'],
            'deduplicated_native_positive':h['positive'],'repeated_native_positive':other['positive'],
            'deduplicated_evidence_records':len(h['evidence_ids']),'repeated_evidence_records':len(other['evidence_ids']),
            'deduplicated_source_groups':len(h['dependence_groups']),'repeated_source_groups':len(other['dependence_groups']),
            'confidence_increased':other['positive']['confidence']>h['positive']['confidence']})
    write_json(out/'ablation-belief-effects.json',{'matched_hypotheses':len(effects),
        'confidence_increased_count':sum(r['confidence_increased'] for r in effects),'rows':effects,
        'scope':'Comparison of native training outputs, not a new TV calculation. Repeated ancestry can raise native confidence without adding independent source groups; unchanged classification metrics do not prove duplication safe.'})
    return audit


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
