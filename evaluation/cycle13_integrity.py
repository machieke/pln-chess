"""Verify source ancestry and bind every experimental field artifact to its receipt."""
import argparse
from pathlib import Path
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle13.ontology import validate_packet
from evaluation.cycle13_data_audit import run as source_audit
from evaluation.cycle13_temporal_audit import run as temporal_audit
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out);source_audit(out,True);temporal_audit(out)
    code=production_code_hash();assert code==read_json(out/'source-freeze.json')['production_code_hash']
    pairs=read_json(out/'features/index.json');temporal=read_json(out/'temporal/features/index.json')
    assert pairs['cases']==340 and temporal['source_games']==60 and temporal['comparisons']==120
    files={}
    for receipt in pairs['records']+temporal['receipts']:
        assert receipt['passed'] and receipt['identity']['production_code_hash']==code
        assert receipt['label_independent'] and not receipt['execution']['truncated']
        path=out/receipt['artifact'];assert sha(path)==receipt['sha256']
        packets=[receipt['packet']] if 'packet' in receipt else [r['packet'] for r in receipt['comparisons']]
        for packet in packets:validate_packet(packet)
        files[receipt['artifact']]=dict(sha256=receipt['sha256'],semantic_sha256=receipt['semantic_sha256'])
    assert len(files)==400
    write_json(out/'datasets/integrity.json',dict(passed=True,production_code_hash=code,
        source_pairs=340,source_games=340,temporal_plans=60,temporal_comparisons=120,
        independent_temporal_games=60,temporal_games_already_counted_in_pairs=True,
        source_and_label_audit_sha256=sha(out/'datasets/audit.json'),
        temporal_audit_sha256=sha(out/'datasets/temporal-audit.json'),
        feature_files=files,reference_labels_used_in_feature_extraction=False,
        source_hash=read_json(out/'datasets/source-pairs.json')['hash'],
        label_hash=read_json(out/'datasets/reference-labels.json')['hash']))
    print('CYCLE 13 DATA AND FEATURE INTEGRITY VERIFIED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
