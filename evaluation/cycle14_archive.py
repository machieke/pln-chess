"""Explicit offline serialization policy for dense registered response audits.

The production store, object encoding and native proofs are unchanged. Bulk
offline audits allow up to ten million expanded object occurrences; interactive
archive export keeps its two-million occurrence limit. Shared storage never
deduplicates an evidence occurrence from the canonical reconstructed stream.
"""
from pln_chess.cycle14.proofs import ProofError, ProofStore


OFFLINE_OCCURRENCE_LIMIT = 10_000_000


class OfflineAuditStore(ProofStore):
    def canonical_chunks(self, root, *, max_nodes=OFFLINE_OCCURRENCE_LIMIT, **kwargs):
        if type(max_nodes) is not int or not 0 < max_nodes <= OFFLINE_OCCURRENCE_LIMIT:
            raise ProofError('Invalid offline proof occurrence budget')
        yield from super().canonical_chunks(root, max_nodes=max_nodes, **kwargs)


def archive_census(archive):
    """Count every expanded object occurrence, retaining ordered repeats."""
    from pln_chess.cycle14.proofs import dependencies
    memo={}
    def count(identifier):
        if identifier not in memo:
            memo[identifier]=1+sum(count(child) for child in dependencies(archive['objects'][identifier]))
        return memo[identifier]
    occurrences=count(archive['root'])
    assert occurrences<=OFFLINE_OCCURRENCE_LIMIT
    return dict(unique_objects=len(archive['objects']),expanded_object_occurrences=occurrences,
        offline_occurrence_limit=OFFLINE_OCCURRENCE_LIMIT,interactive_default_occurrence_limit=2_000_000,
        within_interactive_default_limit=occurrences<=2_000_000)
