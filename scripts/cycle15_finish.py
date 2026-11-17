"""Complete local verification and packing after the full preservation run."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.pln import Runtime
from scripts.cycle15_baseline import sha
from scripts.cycle15_evidence import build,load,restore,verify


def run(out):
    out=Path(out).resolve()
    while not (out/'preservation/verified.json').exists():
        failures=[p for p in (out/'preservation/commands').glob('*.json') if read_json(p)['returncode']]
        if failures:raise RuntimeError('Preservation failure requires inspection: '+str(failures))
        time.sleep(30)
    preservation=read_json(out/'preservation/verified.json');assert preservation['passed']
    print('Complete preservation receipt verified; starting isolated benchmarks',flush=True)
    from evaluation.cycle15_performance import run as benchmark
    if not (out/'performance/summary.json').exists():benchmark(out/'performance')
    runtime=Runtime();assert runtime.manifest==read_json(out/'baseline.json')['runtime']
    assert production_code_hash()=='e88ff7969885be101af2ceedbbdf5d5499f4253b361a8cee18ff1814f055282c'
    protected=read_json(out/'protected-files.json')
    changes=[path for path,wanted in protected.items() if sha(ROOT/path)!=wanted]
    assert not changes,changes
    write_json(out/'historical-files-final.json',dict(passed=True,files=len(protected),changed=changes,
        scope='Final rehash after all historical tests and native experiments finished',completed_unix=time.time()))
    from scripts.cycle14_evidence import load_manifest,verify as verify_c14
    original=verify_c14(ROOT,load_manifest(ROOT/'publication/cycle14/manifest.json'))
    assert original['passed'];write_json(out/'historical-cycle14-final.json',original)
    assert read_json(out/'reproduction/verified.json')['passed']
    assert read_json(out/'supplement/proof-audit.json')['passed']
    assert read_json(out/'supplement/information/field-information-loss.json')['passed']
    assert read_json(out/'supplement/timeout-control.json')['passed']
    import xml.etree.ElementTree as ET
    tests={}
    for name in ('research-tests-final.xml','transport-tests.xml'):
        document=ET.parse(out/name).getroot()
        assert all(int(s.get('errors',0))==int(s.get('failures',0))==0 for s in document.iter('testsuite'))
        tests[name]=sum(int(s.get('tests',0)) for s in document.iter('testsuite'))
    write_json(out/'acceptance.json',dict(passed=True,engineering_packages=8,
        full_legal_preservation=preservation,final_supplemental_tests=tests,
        operational_source_hash=production_code_hash(),runtime=runtime.manifest,
        historical_files=len(protected),cycle14_evidence_files=original['files'],remote_write_performed=False,
        native_execution=True,native_schema_binding=True,native_learning=True,
        chess_scope='One intervening cell positive; occupied-ray negative; longer empty path unsupported',
        architecture_decision='Outcome 2: native binding works; raw chess consequence remains partial',
        research_outcomes_independent_of_engineering_status=True,
        final_source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        acceptance_scope='Complete legal/tests at preserved source plus final isolated research/transport tests; no operational source change',
        completed_unix=time.time()))
    # Only small summaries and manifests enter Git. All native bulk stays local.
    copies=['acceptance.json','historical-files-final.json','historical-cycle14-final.json',
        'performance/summary.json','performance/proof-integrity.json','preservation/verified.json',
        'reproduction/verified.json','transport-tests.xml']
    for relative in copies:
        target=ROOT/'artifacts/cycle15'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(out/relative,target)
    manifest=ROOT/'publication/cycle15/manifest.json'
    if not manifest.exists():
        print('Packing local evidence',flush=True)
        build(out,out/'packs',manifest)
    m=load(manifest)
    assert verify(out,m)['passed']
    restored=restore(out/'restored-evidence',out/'packs',m)
    write_json(ROOT/'artifacts/cycle15/restoration.json',dict(**restored,manifest_sha256=sha(manifest),
        counts=m['counts'],local_packs=str(out/'packs'),restore_root=str(out/'restored-evidence'),
        remote_published=False,scope='Actual complete local pack restore and file-by-file checksum verification'))
    print('CYCLE 15 LOCAL ACCEPTANCE AND RESTORATION COMPLETE',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
