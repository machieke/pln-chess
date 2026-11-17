"""Local publication integrity, using real pack bytes and corruption controls."""
import copy
import json
from pathlib import Path
import pytest
from scripts.cycle15_evidence import build,load,restore,verify


def pack(tmp_path):
    source=tmp_path/'source';(source/'capabilities').mkdir(parents=True)
    (source/'capabilities/a.json').write_text('{"native": "exact evidence"}\n')
    (source/'capabilities/b.json').write_bytes((source/'capabilities/a.json').read_bytes())
    packs=tmp_path/'packs';manifest=tmp_path/'manifest.json'
    build(source,packs,manifest)
    return source,packs,load(manifest)


def test_local_pack_exact_deduplicated_restoration(tmp_path):
    source,packs,manifest=pack(tmp_path);target=tmp_path/'restored'
    assert manifest['counts']['unique_objects']==1 and manifest['counts']['files']==2
    assert restore(target,packs,manifest)['passed']
    assert restore(target,packs,manifest)['passed']
    assert (target/'capabilities/a.json').read_bytes()==(source/'capabilities/a.json').read_bytes()


def test_corrupt_pack_and_conflicting_file_cannot_replace_evidence(tmp_path):
    _,packs,manifest=pack(tmp_path);target=tmp_path/'target'
    archive=packs/manifest['assets'][0]['name'];original=archive.read_bytes()
    archive.write_bytes(original+b'corruption')
    with pytest.raises(ValueError,match='checksum'):restore(target,packs,manifest)
    assert not target.exists()
    archive.write_bytes(original);(target/'capabilities').mkdir(parents=True)
    victim=target/'capabilities/a.json';victim.write_text('existing evidence')
    with pytest.raises(ValueError,match='replace'):restore(target,packs,manifest)
    assert victim.read_text()=='existing evidence'


def test_manifest_escape_and_symlink_parent_rejected(tmp_path):
    _,packs,manifest=pack(tmp_path)
    invalid=copy.deepcopy(manifest);invalid['files'][0]['path']='../escape'
    path=tmp_path/'bad.json';path.write_text(json.dumps(invalid))
    with pytest.raises(ValueError):load(path)
    target=tmp_path/'target';target.mkdir();outside=tmp_path/'outside';outside.mkdir()
    (target/'capabilities').symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError,match='Symlink'):restore(target,packs,manifest)
    assert not list(outside.iterdir())
