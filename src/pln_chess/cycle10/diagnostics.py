"""Fixed-path external research reports, independent of native inference decisions."""
import hashlib
import json
import lzma
import math
import os
from pathlib import Path
from types import SimpleNamespace
from pln_chess.common import ROOT,read_json

SECTIONS={'summary':'analysis/frozen-summary.json','provenance':'sources/manifest.json',
    'failures':'analysis/frozen-failure-index.json','calibration':'calibration/results.json',
    'comparisons':'adaptation/comparison.json','dependence':'dependence/predictions.json',
    'temporal':'temporal/summary.json','performance':'performance/comparison.json',
    'identity':'verification.json','architecture':'architecture/decision.json'}
ARMS=('frozen','small','large','temporal')


def output_root():return Path(os.environ.get('C10_OUT',ROOT/'artifacts/cycle10'))


def report(section='summary',arm='frozen'):
    if section not in SECTIONS or arm not in ARMS:raise ValueError('Unknown external report or model arm')
    relative=SECTIONS[section]
    if section in ('summary','failures'):relative=relative.replace('frozen-',arm+'-')
    path=output_root()/relative
    if not path.exists():return dict(available=False,section=section,arm=arm,reason='This study artifact has not been generated.')
    return dict(available=True,section=section,arm=arm,artifact=relative,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        native=False,data=read_json(path),scope='Recorded empirical diagnostics; calibrated frequencies do not change native truth values, classifications or proof status.')


def _record(relative,index):
    if type(index) is not int or index<0:raise ValueError('Invalid recorded case index')
    path=output_root()/relative;records=json.loads(lzma.decompress(path.read_bytes()))
    if index>=len(records):raise ValueError('Recorded case index is outside this study')
    return dict(index=index,artifact=relative,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),data=records[index])


def failure_proof(index,arm='frozen'):
    if arm not in ARMS:raise ValueError('Unknown experimental model arm')
    return _record(f'analysis/{arm}-failure-proofs.json.xz',index)


def temporal_control(index):return _record('temporal/counterfactuals.json.xz',index)


def game_index():
    data=read_json(output_root()/'datasets/dataset.json')
    return dict(dataset_hash=data['hash'],games=[dict(id=g['id'],source=g['source_collection'],split=g['split'],
        plies=len(g['moves']),complete=g['complete'],headers=g['headers']) for g in data['games']])


def recorded_history(game_id,ply=None):
    from pln_chess.cycle10.temporal import replay_game
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.pln import Runtime
    game=next((g for g in read_json(output_root()/'datasets/dataset.json')['games'] if g['id']==game_id),None)
    if game is None:raise ValueError('Unknown recorded game identity')
    rt=Runtime();model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    return replay_game(game,len(game['moves']) if ply is None else ply,model.version,rt.version)


def _calibration():
    out=output_root();path=out/'calibration/results.json';acceptance=out/'acceptance.json'
    if not path.exists() or not acceptance.exists():return None
    receipt=read_json(acceptance);raw=path.read_bytes()
    if receipt.get('passed') is not True or hashlib.sha256(raw).hexdigest()!=receipt.get('calibration_sha256'):return None
    return json.loads(raw)


def calibrated_diagnostic(candidate,calibration=None):
    unavailable=dict(available=False,native=False,changes_classification=False)
    from pln_chess.cycle10.acceptance import accepted_model
    calibration=calibration or _calibration()
    identity=SimpleNamespace(version=candidate.get('model_version'),runtime_version=candidate.get('runtime_version'))
    if not calibration or not accepted_model(identity):return {**unavailable,'reason':'Source-bound external calibration receipt unavailable'}
    if candidate.get('model_version')!=calibration['model_version'] or candidate.get('mode')!='operational':
        return {**unavailable,'reason':'Calibration applies only to the frozen operational model'}
    if (candidate.get('temporal_evidence') or {}).get('mode','fen-only')!='fen-only':
        return {**unavailable,'reason':'This mapping was fitted on FEN-only inference; supplied-history calibration is unvalidated'}
    if candidate.get('classification')=='incomplete' or not candidate.get('raw_stv'):
        return {**unavailable,'reason':'No complete native diagnostic channel'}
    population='in-board' if candidate.get('observations',{}).get('context',{}).get('destination_exists') is True else 'complete'
    index=min(9,max(0,int(candidate['raw_stv']['strength']*10)))
    old=calibration['frozen_mapping'][population][index];external=calibration['external_mapping'][population][index]
    if any(not math.isfinite(m['probability']) or not 0<=m['probability']<=1 for m in (old,external)):
        raise ValueError('Invalid external diagnostic frequency')
    return dict(available=True,native=False,changes_classification=False,population=population,
        frozen_C9_frequency=old['probability'],external_validation_frequency=external['probability'],
        external_bin_count=external['n'],fit_split=calibration['fit_split'],fit_games=calibration['fit_games'],
        dataset_hash=calibration['dataset_hash'],model_version=calibration['model_version'],
        scope='Separate empirical frequency estimates; neither is a native STV, confidence interpretation or complete legality proof.')


def decorate_inspection(result):
    calibration=_calibration()
    def decorate(value):
        if 'comparisons' in value:return {**value,'comparisons':{k:decorate(v) for k,v in value['comparisons'].items()}}
        def candidate(c):return {**c,'external_diagnostics':calibrated_diagnostic(c,calibration)}
        if 'candidate' in value:return {**value,'candidate':candidate(value['candidate'])}
        if 'candidates' in value:return {**value,'candidates':[candidate(c) for c in value['candidates']]}
        return value
    return decorate(result)
