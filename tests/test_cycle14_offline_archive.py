"""Offline dense archives preserve the production encoding and resource caps."""
import hashlib

import pytest

from evaluation.cycle14_archive import OfflineAuditStore
from pln_chess.common import canonical
from pln_chess.cycle14.proofs import ProofError, ProofStore


def test_dense_shared_evidence_round_trip_and_default_limit():
    # Only three unique objects, but over two million ordered occurrences.
    # Compute expected bytes independently without building the expanded tree.
    value={'evidence_ids':['same-source']}
    copies=1_000_001
    expected=hashlib.sha256()
    expected.update(b'[')
    item=canonical(value).encode()
    for index in range(copies):
        if index:expected.update(b',')
        expected.update(item)
    expected.update(b']')
    with OfflineAuditStore() as store:
        child=store.put(value)
        root=store.put([child]*copies)
        with pytest.raises(ProofError,match='node budget'):
            b''.join(store.canonical_chunks(root,max_nodes=2_000_000))
        archive=store.archive(root)
        assert archive['canonical_legacy_sha256']==expected.hexdigest()
    with ProofStore() as interactive:
        with pytest.raises(ProofError,match='node budget'):
            interactive.import_archive(archive)
        assert interactive.census()['host_stored_objects']==0
    with OfflineAuditStore() as restored:
        assert restored.import_archive(archive).id==root.id
        assert restored.legacy_digest(root)==expected.hexdigest()
        for limit in (True,0,-1,10_000_001):
            with pytest.raises(ProofError,match='budget'):
                b''.join(restored.canonical_chunks(root,max_nodes=limit))
