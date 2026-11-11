"""Bind recorded browser observations and the actual raw download to frozen source."""
import argparse
import json
import lzma
from pathlib import Path
import subprocess
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out).resolve();ui=out/'ui';code=production_code_hash()
    freeze=read_json(out/'source-freeze.json');assert freeze['production_code_hash']==code
    obs={p.stem:read_json(p) for p in (ui/'observations').glob('*.json')}
    for row in obs.values():
        assert row['noHorizontalOverflow'] and row['boardCells']==[64,64]
        assert not row['execution']['truncated'] and not row['execution'].get('error')
        assert row['models']['legal']==read_json(out/'baseline/reproduction-receipt.json')['identity']['accepted_model']
        assert all(not p['jointComplete'] for p in row['preferences'])
    trained=obs['reversed-with-legal-values'];empty=obs['empty-complete']
    assert trained['legalCandidates']==empty['legalCandidates']
    assert trained['preferences'][0]['status']=='B-preferred' and empty['preferences'][0]['status']=='indeterminate'
    assert obs['original-complete']['preferences'][0]['status']=='A-preferred'
    assert read_json(ui/'real-query-reversal.json')['passed']
    temporal=obs['temporal-desktop'];mobile=obs['temporal-mobile']
    assert len(temporal['stateNames'])==7 and temporal['width']==1280 and mobile['width']==390
    assert temporal['rawSha256']==mobile['rawSha256']
    assert [(p['horizon'],p['status']) for p in temporal['preferences']]==[(2,'B-preferred'),(3,'indeterminate')]
    assert temporal['unexaminedResponses']
    export=read_json(ui/'export/verified.json');assert export['passed'] and export['exact_response_bytes']
    archive=ui/'export/pln-cycle13-temporal-proof.json.xz'
    assert sha(archive)==export['compressed_sha256'] and export['raw_sha256']==temporal['rawSha256']
    assert export['validation']==dict(graphs=10,proof_ids=607,all_valid=True)
    sessions=[]
    for directory in sorted(ui.glob('2026-*')):
        summary=(directory/'SUMMARY.md').read_text()
        assert 'No console errors detected.' in summary and 'No server errors detected.' in summary
        meta=read_json(directory/'metadata.json')
        assert not subprocess.check_output(['git','diff','--name-only','3e5aae6b6e4989cc8f0a5ad4eafcbd7df352f9dc',meta['commitSha'],'--','src'],cwd=ROOT,text=True)
        video=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(directory/'session.webm')],text=True))['format']
        assert float(video['duration'])>0
        actions=read_json(directory/'session-log.json')
        sessions.append(dict(path=str(directory.relative_to(out)),source_head=meta['commitSha'],
            action_count=len(actions),screenshots=len(list(directory.glob('*.png'))),
            encoded_video_seconds=float(video['duration']),video_sha256=sha(directory/'session.webm'),
            console_errors=0,server_errors=0,summary_sha256=sha(directory/'SUMMARY.md')))
    assert len(sessions)==2
    detail=obs['concept-proof-detail'];assert detail['proofPage'].startswith('Page 1 of 14')
    assert detail['preferences'][0]['status']=='A-preferred'
    assert read_json(ui/'owned-process-cleanup.json')['passed']
    write_json(ui/'verification.json',dict(passed=True,production_code_hash=code,
        skill='/home/purplezky/.codex/skills/proofshot/SKILL.md',sessions=sessions,
        real_native_http_requests=True,trained_preference=True,evidence_removal=True,
        fixed_order_legal_candidate_parity=True,reversal=True,bounded_continuations=True,
        desktop_and_mobile=True,concept_field_and_preference_proof_inspection=True,
        raw_download=export,observations={p.name:sha(p) for p in sorted((ui/'observations').glob('*.json'))},
        visual_review='visual-review.md',cleanup='owned-process-cleanup.json',
        recording_limit='Encoded videos are shorter than wall-clock session/action timestamps. Screenshots and timestamped action logs are the authoritative action evidence; no frame-accurate timeline correspondence is claimed.',
        automation_corrections=['Initial legal proof-ID placeholders replaced with complete browser-candidate hashes; original captures retained.',
            'Cross-order legacy legal DAG aliases can differ; exact legal-candidate parity checked under fixed order.',
            'First final-session concept selector missed its button; supplemental recorded session used the card button selector.',
            'Attempt to JSON-parse one paginated concept fragment failed; full response and visible concept identity were checked instead.'],
        limitations=['Illustration cases were selected after outcomes and are not evaluation samples.',
            'Native conditional proofs remain partial strategic arguments; no move is selected.']))
    print('RECORDED BROWSER AND EXACT EXPORT VERIFIED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
