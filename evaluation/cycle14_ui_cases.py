"""Choose a disclosed training illustration for native evidence removal in UI."""
import argparse
from pathlib import Path

from pln_chess.common import read_json,digest
from pln_chess.pln import Runtime
from pln_chess.cycle14.model import PreferenceModel
from pln_chess.cycle14.inference import infer_preferences
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out);runtime=Runtime();registry=read_json(out/'model/registry.json')
    entry=registry['models'][registry['primary_immediate']]
    model=PreferenceModel.load(out/entry['path'],runtime)
    sources={r['id']:r for r in read_json(out/'datasets/source-pairs.json')['records'] if r['split']=='train'}
    generation=read_json(out/'features/selected-generations.json')['immediate']
    features=read_json(out/'features'/generation/'index.json')
    rows=sorted((r for r in features['records'] if r['id'] in sources),key=lambda r:digest(['c14-ui-training-illustration',r['id']]))
    chosen=None;inspected=0
    for start in range(0,len(rows),32):
        batch=rows[start:start+32]
        native=infer_preferences([r['observations'][0]['packet'] for r in batch],model,runtime=runtime)
        assert not native['execution']['truncated']
        inspected+=len(batch)
        for record,prediction in zip(batch,native['comparisons']):
            if prediction['status'] in ('A-preferred','B-preferred') and prediction['conditional_proof_complete']:
                chosen=dict(source=sources[record['id']],expected_channels=prediction['channels'],
                    expected_status=prediction['status'],native_prediction=prediction,
                    feature_archive=record['archive'],feature_archive_sha256=record['archive_sha256'])
                break
        if chosen:break
    atomic_json(out/'ui/training-illustration.json',dict(passed=True,selected=chosen,training_packets_inspected=inspected,
        model_version=model.version,runtime_version=runtime.version,driver_sha256=sha(__file__),
        reference_labels_used_in_selection=False,final_test_cases_used=False,
        scope='First supported native conditional in deterministic hash order among training observations, solely to exercise UI evidence display/removal. Selection uses model output, never reference agreement. This illustration is not held-out accuracy or generalization evidence.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');run(parser.parse_args().out)
