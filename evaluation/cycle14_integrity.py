"""Bind frozen partitions, label revisions and all compact feature inputs."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
from pln_chess.common import ROOT,digest,read_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle14.ontology import validate_packet
from training.cycle14_sources import components
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out);data=read_json(out/'datasets/source-pairs.json');rows=data['records']
    assert digest({k:v for k,v in data.items() if k!='hash'})==data['hash']
    assert len(rows)==940 and sum(r['generation']=='new-c14' for r in rows)==600
    assert len(components(rows))==940
    assert all(len({r['split'] for r in component})==1 for component in components(rows))
    assert sum(r['split']=='test' for r in rows)==200
    assert all(sha(ROOT/path)==value for path,value in read_json(out/'baseline/manifest.json')['protected_files'].items())
    plans=read_json(out/'datasets/temporal-plans.json');assert len(plans['records'])==240
    assert sum(r['split']=='test' for r in plans['records'])==50
    sources={r['id']:r for r in rows};features=[];labels=[];selected=read_json(out/'features/selected-generations.json')
    for kind in ('immediate','temporal'):
        index=read_json(out/'features'/selected[kind]/'index.json')
        assert index['cases']==(940 if kind=='immediate' else 240)
        assert len({r['id'] for r in index['records']})==index['cases']
        assert index['comparisons']==(940 if kind=='immediate' else 480)
        for receipt in index['records']:
            assert receipt['passed'] and receipt['label_independent'] and not receipt['reference_labels_used']
            assert sha(out/receipt['archive'])==receipt['archive_sha256']
            for observation in receipt['observations']:validate_packet(observation['packet'])
            features.append(dict(id=receipt['id'],kind=kind,archive=receipt['archive'],sha256=receipt['archive_sha256'],complete=receipt['complete'],semantic_sha256=receipt['semantic_sha256']))
        generation=read_json(out/f'labels/{kind}-g1/index.json')
        assert len(generation['records'])==(940 if kind=='immediate' else 480)
        for row in generation['records']:
            assert row['evidence_id']=='c14-reference:'+digest({k:v for k,v in row.items() if k!='evidence_id'})
            raw=generation['raw_manifest'][row['id']];assert sha(out/raw['path'])==raw['sha256']
            assert row['inference_prediction_used'] is False
        labels.append(dict(kind=kind,N=len(generation['records']),counts=generation['counts'],semantic_hash=generation['semantic_hash'],actual_reported_nodes=generation['actual_reported_nodes']))
    atomic_json(out/'datasets/integrity.json',dict(passed=True,production_code_hash=production_code_hash(),
        root_pairs=940,new_pairs=600,independent_ancestry_groups=940,partitions=dict(Counter(r['split'] for r in rows)),
        source_hash=data['hash'],partition_sha256=sha(out/'datasets/partitions.json'),overlap_sha256=sha(out/'datasets/overlap-audit.json'),
        temporal_groups=240,new_temporal_groups=180,final_temporal_groups_each_horizon=50,horizons_are_dependent=True,
        features=features,labels=labels,reference_labels_used_in_extraction=False,
        incomplete_feature_counts=dict(Counter(r['kind'] for r in features if not r['complete'])),
        scope='All registered pairs and horizons retained. Missing endpoints remain incomplete; no success-based case filtering.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');run(parser.parse_args().out)
