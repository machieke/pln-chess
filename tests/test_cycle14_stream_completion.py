"""A late cached join must preserve successful receipts and reject mismatches."""
import pytest

from scripts.cycle14_replay_stream import complete_shard


def identity(wrapper='first'):
    return dict(wrapper_sha256=wrapper,proof_driver_sha256='frozen-native-verifier',
        production_code_hash='frozen-production',source_head='frozen-source',
        runtime={'version':'pinned'},shard=1,shards=3,subshard=0,subshards=1)


def test_cached_completion_preserves_original_receipt_and_timing(tmp_path):
    path=tmp_path/'completed.json'
    assert complete_shard(path,identity(),385,100,900)
    original=path.read_bytes()
    assert not complete_shard(path,identity('new-host-wrapper'),385,8,0)
    assert path.read_bytes()==original


@pytest.mark.parametrize('change',['native-verifier','archive-count'])
def test_incompatible_completion_is_rejected_without_mutation(tmp_path,change):
    path=tmp_path/'completed.json';complete_shard(path,identity(),385,100,900)
    original=path.read_bytes();candidate=identity('new-host-wrapper')
    if change=='native-verifier':candidate['proof_driver_sha256']='changed-native-verifier'
    with pytest.raises(AssertionError):
        complete_shard(path,candidate,384 if change=='archive-count' else 385,8,0)
    assert path.read_bytes()==original
