# Publication and evidence availability

The authorized destination is `machieke/pln-chess`, using the dedicated
`cycle17-shared-evidence-semantics` branch descended from
`63fbf4a198d15cc27c8ad15865be84bfdb871c28`. The scientific source freeze is
`fb1981a52efdfe6b901c3aeae4f8205630f1d5b8`. Later commits add delivery tooling,
reports and evidence; the frozen scientific source remains byte-identical.

Ordinary Git includes source and tests, the complete frozen root manifest, small
experimental checkpoints, learning ledgers/revision receipts, compact result
tables, decisive native programs and output, reproduction commands and the local
bulk manifest. The [witness index](../../artifacts/cycle17/witnesses/index.json)
makes the principal shared/disjoint finding inspectable without the development
machine. No native environment, dependency cache, proof database or bulk pack is
added to Git. No historical published commit is rewritten.

The project publication gate checks every new reachable blob across the entire
Cycle 17 range, including content no longer present at the tip. The ceilings are
10 MiB per new blob and 100 MiB total new unique blob content. These are project
budgets, distinct from [GitHub's file-size restrictions](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
The final exact object inventory is generated after the last commit outside the
tracked checkout, so it includes that commit without a self-referential receipt.

Bulk research and preservation data remain at
`/home/purplezky/cycle17-evidence-20261117`. The committed
[manifest](../../publication/cycle17/manifest.json) records file hashes, local pack
hashes and availability. Actual restoration is verified by the
[restoration receipt](../../artifacts/cycle17/restoration.json). Packs are not
remotely uploaded, and no release or paid storage is created. Compact summaries
can refer to original local paths; those paths are provenance, not download links.
The [reproduction guide](reproduction.md) distinguishes the small public experiment
from full historical verification requiring separately obtained packs.

Before publication, the delivery procedure checks source-bound acceptance,
report links, the minimal reproducer, secret-bearing file patterns, clean Git
status, authorized fetch/push URLs, multiple push URLs and applicable URL rewrites.
The initial configuration contains one SSH origin for the authorized repository
and an unrelated dhall-lang rewrite; the remote is checked again before pushing.
The branch push names its destination explicitly, uses no force option, and
changes neither master nor the default branch. Git's explicit refspec and
fast-forward behavior are documented in [git-push](https://git-scm.com/docs/git-push).

Publication is complete only after a fresh remote query returns the final local
SHA. A cached remote-tracking branch is insufficient. The verification also
checks the canonical repository independently and retrieves the engineering
report and minimal-reproducer source at that commit. Remote reference queries
follow [git-ls-remote](https://git-scm.com/docs/git-ls-remote).

The final SHA, exact blob inventory and independent remote-verification receipt
are recorded outside the tracked checkout and in the final delivery response,
as required by the brief. The [acceptance receipt](../../artifacts/cycle17/acceptance.json)
binds the engineering contents; it does not pretend to prove a push performed
after its own commit. A failed remote check would be reported as a blocked push,
never as successful publication.
