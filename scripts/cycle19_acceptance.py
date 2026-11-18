"""Read-only final acceptance: hashes, executable freeze and evidence gates."""
import argparse
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from pln_chess.common import ROOT,read_json,write_json,digest
from research.cycle19.records import sha
from scripts.cycle19_baseline import START

REPORTS=('engineering-report','package-matrix','research-registration','targets-and-measurements',
    'corpus-and-transfer','native-results','evidence-lifecycle','architecture-decision','reproduction','publication')


def check():
    directory=ROOT/'artifacts/cycle19';source=read_json(directory/'source-provenance.json')
    for path,h in source['files'].items():assert sha(ROOT/path)==h,path
    assert source['starting_commit']==START
    assert sha(ROOT/'docs/cycle19/research-registration.md')==source['registration_sha256']
    subprocess.run(['git','merge-base','--is-ancestor',START,'HEAD'],check=True)
    corpus=read_json(directory/'corpus-registration.json');assert corpus['split_counts']==dict(A=24,B=24,development=24,test=56)
    assert corpus['selection_outcomes_accessed'] is False
    history=read_json(directory/'historical-final.json');assert history['passed'] and history['changed']==[]
    assert history['protected_files']==24175
    models=read_json(directory/'learning/models.json')
    from research.cycle15.knowledge import load_rules
    for arm,item in models.items():
        model=item['model'];load_rules(model,path=ROOT/'knowledge/cycle16/finite_two.metta')
        assert model['version']==digest({k:v for k,v in model.items() if k!='version'})
        for name,rule in model['rules'].items():
            assert len(rule['ancestry'])==(0 if arm=='P' else 24)
            assert len(set(rule['ancestry']))==len(rule['ancestry'])
            for ident in rule['evidence']:
                node=model['admitted_components'][ident];assert node['kind']=='annotation'
                assert node['payload']['admitted'] and node['payload']['rule']==name
    measures=read_json(directory/'measurement/episodes.json')
    assert len(measures)==272
    assert sum(e['variant']=='natural' for e in measures)==128
    assert read_json(directory/'measurement/manual-fixtures.json')['passed']
    index=read_json(directory/'evaluation-index.json');assert len(index)==1256
    assert sum(r['variant']=='natural' for r in index)==896
    assert read_json(directory/'lifecycle/summary.json')['passed']
    assert all(read_json(directory/'lifecycle/summary.json')['checks'].values())
    assert read_json(directory/'measurement/query-meaning.json')['status']=='not_identified'
    assert read_json(directory/'anchors/summary.json')['passed']
    for entry in read_json(directory/'demonstrations/index.json').values():
        assert entry['available'] and (ROOT/entry['path']).exists()
    preservation=read_json(directory/'preservation/cycle19-verification.json')
    assert preservation['passed'] and preservation['source_head']==source['source_head']
    for k,v in dict(legal_shards=206,legal_rows=584112,negative_controls=287,history_controls=27,
        recoveries=2,holdouts=76,classification_changes=0,exact_native_proof_parity=True,checkout_clean=True).items():assert preservation[k]==v
    suites=list(ET.parse(directory/'preservation/tests.xml').getroot().iter('testsuite'))
    assert sum(int(s.get('tests',0)) for s in suites)==preservation['tests']
    assert all(int(s.get(k,0))==0 for s in suites for k in ('errors','failures','skipped'))
    reproduction=read_json(directory/'reproduction/verified.json')
    assert reproduction['passed'] and reproduction['source_head']==source['source_head']
    assert reproduction['historical_bulk_and_pgn_access_denied']
    resources=read_json(directory/'resources.json');assert resources['native_reserved']+resources['publication_reserve_calls']<=4000
    assert resources['unreturned_reservations']==0
    restore=read_json(directory/'restoration.json');assert restore['passed'] and not restore['bulk_remote_publication']
    assert sha(ROOT/'publication/cycle19/manifest.json')==restore['manifest_sha256']
    for path,h in read_json(directory/'compact-inventory.json')['files'].items():assert sha(ROOT/path)==h,path
    for name in REPORTS:assert len((ROOT/f'docs/cycle19/{name}.md').read_text())>300
    receipts={str(p.relative_to(ROOT)):sha(p) for p in directory.rglob('*') if p.is_file() and p.name!='acceptance.json'}
    receipts.update({f'docs/cycle19/{n}.md':sha(ROOT/f'docs/cycle19/{n}.md') for n in REPORTS})
    receipts['publication/cycle19/manifest.json']=sha(ROOT/'publication/cycle19/manifest.json')
    return dict(passed=True,starting_commit=START,source_head=source['source_head'],
        prepared_from_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        preservation=preservation,decision='A+B+C+D: measured domain targets and bounded native transfer; probability unidentified; shared evidence and recursive reuse remain blocked',
        publication='Final push and canonical HTTPS retrieval verified separately after final commit',verified_receipt_sha256=receipts)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();value=check()
    target=ROOT/'artifacts/cycle19/acceptance.json'
    if a.write:
        assert not target.exists();write_json(target,value)
    else:assert read_json(target)['verified_receipt_sha256']==value['verified_receipt_sha256']
    print('Cycle19 source-bound engineering acceptance passed')
