"""Read-only empirical reports, separate from native inference and acceptance."""
import hashlib
import json
import lzma
import math
import os
from pathlib import Path
from pln_chess.common import ROOT,read_json


def output_root():return Path(os.environ.get('C9_OUT',ROOT/'artifacts/cycle9'))


def report(section='summary'):
    out=output_root()
    paths={'summary':'analysis/evaluation-summary.json','calibration':'calibration/results.json',
           'failures':'analysis/failure-index.json','performance':'performance/C9-optimized.json',
           'temporal':'temporal/summary.json','identity':'verification.json'}
    if section not in paths:raise ValueError('Unknown Cycle 9 report section')
    path=out/paths[section]
    if not path.exists():return {'available':False,'section':section,'reason':'Run the Cycle 9 study to generate this report.'}
    return {'available':True,'section':section,'artifact':paths[section],
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native':False,'data':read_json(path),
        'scope':'Recorded research diagnostics. Empirical calibration estimates are not native PLN truth values.'}


def failure_proof(index):
    if type(index) is not int or index<0:raise ValueError('Invalid failure index')
    path=output_root()/'analysis/failure-proofs.json.xz'
    rows=json.loads(lzma.decompress(path.read_bytes()))
    if index>=len(rows):raise ValueError('Failure index is outside the recorded study')
    return {'index':index,'native_calibration':False,'data':rows[index]}


def _verified_calibration():
    out=output_root();path=out/'calibration/results.json';acceptance=out/'acceptance.json'
    if not path.exists() or not acceptance.exists():return None,'Verified calibration artifact unavailable'
    receipt=read_json(acceptance)
    raw=path.read_bytes()
    if receipt.get('passed') is not True or hashlib.sha256(raw).hexdigest()!=receipt.get('calibration_sha256'):
        return None,'Calibration artifact integrity is unverified'
    return json.loads(raw),None


def calibrated_diagnostic(candidate, _verified=None):
    unavailable={'available':False,'native':False,'changes_classification':False}
    calibration,error=_verified if _verified is not None else _verified_calibration()
    if error:return {**unavailable,'reason':error}
    if calibration['model_version']!=candidate.get('model_version'):
        return {**unavailable,'reason':'Calibration was fit for a different model'}
    if candidate.get('mode')!='operational':return {**unavailable,'reason':'Calibration was fit for operational diagnostics only'}
    if candidate.get('classification')=='incomplete':return {**unavailable,'reason':'Inference is incomplete'}
    tv=candidate.get('raw_stv')
    if not tv:return {**unavailable,'reason':'No native diagnostic channel'}
    in_board=candidate.get('observations',{}).get('context',{}).get('destination_exists')
    population='in-board' if in_board is True else 'complete'
    selected=calibration['mappings'][population][min(9,max(0,int(tv['strength']*10)))]
    p=selected['probability']
    if not math.isfinite(p) or not 0<=p<=1:raise ValueError('Invalid empirical diagnostic estimate')
    return dict(available=True,native=False,changes_classification=False,estimated_legal_frequency=p,
        calibration_bin_count=selected['n'],calibration_bin_legal=selected['legal'],population=population,
        fit_games=calibration['fit_games'],fit_positions=calibration['fit_positions'],fit_split=calibration['fit_split'],
        dataset_hash=calibration['dataset_hash'],model_version=calibration['model_version'],
        scope='Frequency estimate from separate synthetic calibration games; not a native STV or proof of legality. Distribution shift remains possible.')


def decorate_inspection(result, _verified=None):
    # Validate/read one calibration artifact per response, including comparisons.
    verified=_verified if _verified is not None else _verified_calibration()
    if 'comparisons' in result:
        return {**result,'comparisons':{k:decorate_inspection(v,verified) for k,v in result['comparisons'].items()}}
    def decorate(candidate):
        from pln_chess.cycle9.temporal import temporal_categories
        history=candidate.get('temporal_evidence')
        return {**candidate,'research_diagnostics':dict(model_version=candidate.get('model_version'),
            runtime_version=candidate.get('runtime_version'),mode=candidate.get('mode'),
            calibrated=calibrated_diagnostic(candidate,verified),
            temporal_categories=temporal_categories(history) if history and history.get('schema')=='history-v6.1' else None)}
    if 'candidate' in result:return {**result,'candidate':decorate(result['candidate'])}
    if 'candidates' in result:return {**result,'candidates':[decorate(c) for c in result['candidates']]}
    return result
