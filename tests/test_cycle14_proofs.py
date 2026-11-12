import copy
import zlib

import pytest

from pln_chess.common import canonical,digest
from pln_chess.cycle14.proofs import ProofStore,ProofError,Ref


def test_exact_round_trip_preserves_distinct_evidence_and_repeated_occurrences(tmp_path):
    first=dict(operator='Truth_ModusPonens',truth_value=dict(strength=.8,confidence=.4),evidence_ids=['one'])
    second={**first,'evidence_ids':['two']}
    value=dict(proofs=[first,second,first],native_expression='(Truth_ModusPonens (stv 1 0.99) (stv .8 .4))',
        literal={'$ref':'ordinary user data'},unknown=None,position=[(1,2)],negative_zero=-0.0)
    with ProofStore(tmp_path/'proofs.sqlite') as store:
        root=store.put(value)
        assert canonical(store.expand(root))==canonical(value)
        assert b''.join(store.canonical_chunks(root))==canonical(value).encode()
        assert store.legacy_digest(root)==digest(value)
        assert store.put(first)!=store.put(second)
        assert store.put(first)==store.put(copy.deepcopy(first))
        handle=store.publish(root,{'status':'indeterminate'},{'history':['e2e4'],'model':'frozen'})
        archive=store.archive(root)
    with ProofStore(tmp_path/'proofs.sqlite') as restarted:
        assert restarted.request(handle)['root']==root.id
        assert canonical(restarted.expand(root))==canonical(value)
    with ProofStore() as fresh:
        restored=fresh.import_archive(archive)
        assert fresh.legacy_digest(restored)==digest(value)
        assert len(fresh.expand(restored)['proofs'])==3


def test_references_allow_streaming_assembly_without_building_nested_responses():
    with ProofStore() as store:
        proof=store.put({'native_expression':'(Truth_Negation (stv 1 .9))','evidence_ids':['source']})
        state=store.put({'relations':[proof,proof]})
        response=store.put({'A':state,'B':state})
        expected={'A':{'relations':[store.expand(proof)]*2},'B':{'relations':[store.expand(proof)]*2}}
        assert store.legacy_digest(response)==digest(expected)
        page=store.page(response,limit=2)
        assert len(page['nodes'])==2 and page['next_offset']==2
        assert page['native_resident'] is False


@pytest.mark.parametrize('corruption',['missing','bytes','valid-json-wrong-identity'])
def test_corruption_fails_explicitly_even_after_a_successful_read(corruption):
    with ProofStore() as store:
        child=store.put({'evidence':'original'});root=store.put([child])
        store.expand(root)
        if corruption=='missing':store.db.execute('DELETE FROM objects WHERE id=?',(child.id,))
        else:
            payload=b'bad' if corruption=='bytes' else zlib.compress(b'["scalar","tampered"]')
            store.db.execute('UPDATE objects SET payload=? WHERE id=?',(payload,child.id))
        with pytest.raises(ProofError):store.expand(root)
        with pytest.raises(ProofError):store.archive(root)


def test_import_validation_is_atomic_and_unknown_handles_are_errors():
    with ProofStore() as original:
        root=original.put({'premise':{'evidence':'one'}});archive=original.archive(root)
    altered=copy.deepcopy(archive);altered['canonical_legacy_sha256']='0'*64
    altered['manifest_sha256']=digest({k:v for k,v in altered.items() if k!='manifest_sha256'})
    with ProofStore() as target:
        with pytest.raises(ProofError,match='Reconstructed'):target.import_archive(altered)
        assert target.census()['host_stored_objects']==0
        with pytest.raises(ProofError,match='Unknown'):target.request('proof-request:missing')
        target.import_archive(archive)
        with pytest.raises(ProofError):target.put({'missing':Ref('0'*64)})


def test_request_cache_includes_history_model_and_branch_identity(tmp_path):
    with ProofStore(tmp_path/'cache.sqlite') as store:
        root=store.put({'proof':'original'})
        identity={'history':['e2e4'],'model':'one','branches':[['e7e5']],'complete':True}
        store.publish(root,{'status':'indeterminate'},identity)
        assert store.lookup(identity)['root']==root.id
        for key,value in [('history',[]),('model','two'),('branches',[['c7c5']]),('complete',False)]:
            assert store.lookup({**identity,key:value}) is None
        with pytest.raises(ProofError,match='Conflicting'):
            store.publish(root,{'status':'A-preferred'},identity)


def test_cycles_nonfinite_numbers_and_invalid_pagination_are_rejected():
    with ProofStore() as store:
        cycle=[];cycle.append(cycle)
        with pytest.raises(ProofError,match='Cyclic'):store.put(cycle)
        with pytest.raises(ValueError):store.put({'value':float('nan')})
        root=store.put({'execution':{'time':123},'proof':{'evidence_ids':['x']}})
        assert store.legacy_digest(root,omit_keys=('execution',))==digest({'proof':{'evidence_ids':['x']}})
        with pytest.raises(ProofError):store.page(root,limit=0)
