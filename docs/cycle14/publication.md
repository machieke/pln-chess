# Cycle 14 publication and evidence restoration

Cycle 14's code, models, reports and small verification records are distributed in
Git. Larger frozen evidence is distributed through the
[Cycle 14 evidence release](https://github.com/machieke/pln-chess/releases/tag/cycle14-evidence-v1).
This packaging change does not change scientific inputs, predictions, native
proofs, historical evidence, or the accepted legal model.

## Restore the evidence

From a checkout of the published Cycle 14 branch, use Python 3.12 or newer:

```bash
python3 -m scripts.cycle14_evidence fetch
python3 -m scripts.cycle14_evidence verify
```

The command restores the original `artifacts/cycle14/` paths. It checks each
release pack's SHA-256 and then each restored file's size and SHA-256. Existing
matching files are reused. Different existing files, unsafe paths, symlinks,
unexpected archive entries, missing objects and corrupt downloads fail explicitly.
It never replaces different evidence. Interrupted downloads can be retried;
completed verified packs are reused. A partial pack is downloaded again.

Packs are cached under `~/.cache/pln-chess/cycle14-evidence-v1`; use `--cache PATH`
to choose another disk. Allow approximately 12 GiB for the restored evidence and
another 12 GiB for cached packs. The published baseline's historical files and the
Git object database require additional space. After successful verification,
cached packs may be removed; the restored evidence remains available.

For offline restoration, download the release's `cycle14-evidence-*.tar` assets
to one directory and run:

```bash
python3 -m scripts.cycle14_evidence fetch --asset-dir /path/to/release-assets
```

The evidence is required before running the complete Cycle 14 research
reproduction or following local links to externalized files. Routine source
review and the checked-in reports do not require downloading it. The
[manifest](../../publication/cycle14/manifest.json) lists every original evidence
path, file hash, original Git blob ID, and storage location. Deduplication stores
identical payloads once per release; restoration recreates every original path.

## Original source-bound commit IDs

Only the 60 previously unpublished Cycle 14 commits were repackaged. The published
baseline `54353579e7921f9b47f43bbde1aa61cb887bc6e4` and its ancestors are unchanged.
The [commit mapping](../../publication/cycle14/commit-map.json) relates original
and publication commit IDs. For every mapped commit, metadata, commit message and
all tree entries outside the externalized evidence paths are identical. Additional
publication commits add the downloader, manifests, documentation and transport
tests.

Original verification receipts still describe the original checkouts and retain
their original commit IDs. They are historical records, including their accurate
statements that no push had occurred at the original delivery date. They are not
rewritten to claim that the new publication commits ran the original experiments.

The original history is also preserved in an incremental Git bundle, split into
release assets. It includes all 60 original commits and their evidence versions,
and requires the unchanged published baseline. To make those exact original
source commits available locally without changing the current checkout:

```bash
python3 -m scripts.cycle14_evidence history
```

This optional command verifies every part and the assembled bundle, checks Git's
bundle prerequisites, and imports `refs/archive/cycle14-original-20261116`. The
original delivery tip remains `4a603722a73f9f0280e5034186ee4dc26b0f1bbc`. Full
source-bound reproduction commands that check out original commit IDs should run
this command first. `--asset-dir` and `--cache` are supported here as well.
History restoration needs additional disk space for the split parts, assembled
bundle and imported Git objects; consult the
[history manifest](../../publication/cycle14/original-history.json) for exact
sizes. Normal evidence inspection does not need this optional history download.

## Verification scope

[Publication verification](../../publication/cycle14/verification.json) records
fresh-checkout evidence restoration, preservation of historical files and the
production source hash, original-history restoration, transport tests, and the
size of the revised Git pack. This is a transport and preservation check. The
original 639-test frozen-source run and scientific reproduction retain their
original scope; they are not represented as new experiment executions.

The local preparation tool is `scripts/cycle14_publication.py`. It creates
deterministic, uncompressed tar containers around the existing bytes, each under
1 GiB. Most proof payloads are already XZ-compressed. It creates a separate
publication branch using an isolated Git index and checks that each history change
only removes explicitly externalized paths from Git storage. A new publication
generation requires a new workspace and release tag; existing frozen packs must
not be overwritten.
