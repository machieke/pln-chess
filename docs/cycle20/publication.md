# Publication and evidence

The feature branch is `cycle20-native-belief-workspaces` in `machieke/pln-chess`. The baseline is `7c06d8e15972e5db2e0932160102dda329c304ab` and the final executable-source freeze is `ec48b4a1e5c7a42bacc3d350a64377cdb94fe49d`. Later commits contain the reports and measured compact evidence. The frozen identity manifest covers the adapter, tests, transport and delivery checks. [Source freeze](../../artifacts/cycle20/source-freeze.json)

The local evidence manifest covers 5,560 files and 5,532 unique content objects. Their logical size is 1,737,158,606 bytes. Pack size is 1,740,810,240 bytes. The delivery restored the files into a new directory and verified their checksums. Bulk data remain local. [Pack manifest](../../publication/cycle20/manifest.json) · [Restore receipt](../../artifacts/cycle20/restoration.json)

Publication checks the full baseline-to-final object range, including superseded blobs, against the 10 MiB per-blob and 100 MiB total budgets. It scans all new blobs for common credential patterns and inspects effective fetch/push destinations and URL rewrites. The explicit feature-branch refspec disables tag following. Independent verification uses a fresh Git remote read, the canonical GitHub reference API, exact-SHA raw content hashes and a newly fetched checkout. That checkout runs batch, combined, continuation, correction, history and residency using verified existing dependencies.

The final SHA and its verification receipt live outside the tracked checkout under `/home/purplezky/cycle20-publication-<final-SHA>/verified.json`. The final delivery gives the exact path and range totals.
