"""Read-only research delivery verification; never a model construction path."""
import argparse
from fractions import Fraction as F
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from pln_chess.common import ROOT,read_json,write_json
from research.cycle18.contracts import sha,identity
from scripts.cycle18_baseline import START

REPORTS=('engineering-report','package-matrix','research-registration','source-evidence-contract',
    'parameter-semantics','source-bound-reference','replay-and-conflict-controls','native-compatibility',
    'architecture-decision','reproduction','publication')


def check():
    directory=ROOT/'artifacts/cycle18'
    source=read_json(directory/'source-provenance.json')
    for path,h in source['files'].items():assert sha(ROOT/path)==h,path
    assert source['starting_commit']==START
    assert sha(ROOT/'docs/cycle18/research-registration.md')==source['registration_sha256']
    subprocess.run(['git','merge-base','--is-ancestor',START,'HEAD'],check=True)
    baseline=read_json(directory/'registration/baseline.json')
    assert sha(ROOT/'artifacts/cycle12/model/C12-default.json')==baseline['legal_checkpoint_sha256']
    assert read_json(ROOT/'artifacts/cycle12/model/C12-default.json')['version']==baseline['legal_semantic_identity']
    from pln_chess.pln import Runtime
    from pln_chess.cycle6.inference import production_code_hash
    Runtime().verify();assert Runtime().manifest==baseline['runtime']
    assert production_code_hash()==baseline['operational_source']
    history=read_json(directory/'historical-final.json');assert history['passed'] and history['changed']==[]
    audit=read_json(directory/'contract/mappings/audit.json')
    assert (audit['preparation_records'],audit['admitted_annotations'],audit['excluded_annotations'])==(432,48,384)
    assert audit['admitted_vector_events']==24 and audit['revision_receipts_verified']==144
    for path,h in audit['source_hashes'].items():assert sha(ROOT/path)==h,path
    summary=read_json(directory/'contract/reference_cases/summary.json');assert len(summary)==72
    for key,row in summary.items():
        fitted=read_json(directory/'contract/reference_cases'/key/'result.json')
        assert fitted['status']=='point_under_declared_model'
        assert fitted['posterior_identity']==identity(fitted['posterior'])==row['posterior_identity']
        assert sum(F(p['probability']) for p in fitted['posterior'])==1
        assert F(fitted['predictive_probability'])==sum(F(p['probability'])*F(p['theta_clear'])*F(p['theta_attack']) for p in fitted['posterior'])
        assert fitted['predictive_probability']==row['probability']
        assert fitted['parameter_generation']['native_checkpoint_reference'] is None
        assert len(set(fitted['event_ids']))==len(fitted['event_ids'])
        assert len(fitted['prior_and_likelihoods'])<=25
        bound=read_json(directory/'contract/reference_cases'/key/'bounds.json')
        assert bound['source_posterior_identity']==fitted['posterior_identity'] and bound['bounds']==row['bounds']
        for name,index in [('lower_witness',0),('upper_witness',1)]:
            plan=bound[name]
            assert sum(F(p['probability']) for p in plan)==1
            assert sum(F(p['probability'])*F(p['theta_clear'])*F(p['theta_attack']) for p in plan)==F(bound['bounds'][index])
            for param,dist in bound['fixed_information'].items():
                for marginal in dist:
                    assert sum(F(p['probability']) for p in plan if p[param]==marginal['value'])==F(marginal['probability'])
    assert read_json(directory/'contract/reference_cases/not-identified.json')['status']=='not_identified'
    controls=read_json(directory/'contract/controls/results.json');assert controls['passed']
    assert controls['copy_conflict']['status']=='inconsistent_evidence' and controls['cycle_evidence_added']==0
    for count in (1,10,100):assert controls['application_repeats'][str(count)]['applications']==count
    replay=read_json(directory/'native/summary.json');assert replay['passed'] and replay['oracle_disabled']
    for arm,record in replay['arms'].items():
        expected='supported-positive' if arm in ('D-AB','D-BA') else 'unknown'
        assert record['stages']['Attack']['classification']==expected
        for stage in record['stages'].values():
            assert stage['exact_channels_and_trace']
            assert sha(directory/'native/raw'/Path(stage['native']['path']).name)==stage['native']['sha256']
    correspondence=read_json(directory/'correspondence.json')
    assert len(correspondence['arms'])==6
    for arm,c in correspondence['arms'].items():
        assert c['directly_comparable_quantities'] is False
        for ref in c['reference'].values():assert sha(ROOT/ref['path'])==ref['sha256']
        for stage in c['native'].values():
            assert stage['application']['observed_parent_refs'] is None
            for event in stage['environmental_events']:
                assert sha(ROOT/event['source_artifact_path'])==event['source_artifact_hash']
    preservation=read_json(directory/'preservation/cycle18-verification.json')
    assert preservation['passed'] and preservation['source_head']==source['source_head']
    for k,v in dict(legal_shards=206,legal_rows=584112,negative_controls=287,history_controls=27,recoveries=2,holdouts=76,
                    classification_changes=0,exact_native_proof_parity=True,checkout_clean=True).items():
        assert preservation[k]==v,(k,preservation[k])
    suites=list(ET.parse(directory/'preservation/tests.xml').getroot().iter('testsuite'))
    assert sum(int(s.get('tests',0)) for s in suites)==preservation['tests']
    assert all(int(s.get(k,0))==0 for s in suites for k in ('errors','failures','skipped'))
    reproduction=read_json(directory/'reproduction/verified.json')
    assert reproduction['passed'] and reproduction['source_head']==source['source_head']
    assert reproduction['historical_bulk_and_pgn_access_denied']
    assert read_json(directory/'resources.json')['budget_passed']
    restore=read_json(directory/'restoration.json');assert restore['passed'] and not restore['bulk_remote_publication']
    assert sha(ROOT/'publication/cycle18/manifest.json')==restore['manifest_sha256']
    for name in REPORTS:
        path=ROOT/f'docs/cycle18/{name}.md';text=path.read_text();assert len(text)>300
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in link and not link.startswith('#'):
                assert (path.parent/link.split('#')[0]).exists(),(name,link)
    receipts={str(p.relative_to(ROOT)):sha(p) for p in directory.rglob('*') if p.is_file() and p.name!='acceptance.json'}
    receipts.update({f'docs/cycle18/{n}.md':sha(ROOT/f'docs/cycle18/{n}.md') for n in REPORTS})
    receipts['publication/cycle18/manifest.json']=sha(ROOT/'publication/cycle18/manifest.json')
    return dict(passed=True,starting_commit=START,source_head=source['source_head'],
        prepared_from_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        preservation=preservation,decision='B + D: executable source-bound hypothetical semantics; native confidence bridge and empirical reliability unidentifiable',
        publication='Final branch push and canonical retrieval verified separately after final commit',verified_receipt_sha256=receipts)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();value=check()
    target=ROOT/'artifacts/cycle18/acceptance.json'
    if a.write:
        assert not target.exists();write_json(target,value)
    else:
        prior=read_json(target);assert prior['verified_receipt_sha256']==value['verified_receipt_sha256']
    print('Cycle 18 source-bound engineering acceptance passed')
