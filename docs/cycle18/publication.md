# Publication and evidence discipline

The authorized destination is exactly `machieke/pln-chess`, on
`cycle18-shared-parameter-contract`, descended from
`24f30ce8d4e0631f8937404929485dfdc0032f93`. The initial branch was the accepted
Cycle 17 branch, with only the new user brief untracked. No unrelated work was
reset. The registration commit precedes reference execution; executable source,
tests and delivery gates are frozen at
`9dc9159de311a2b5304e4051eef2919e7994c19f`. Later commits carry reports and evidence.

Ordinary Git contains source, typed contracts, tests, eleven reports, complete
small mapping records, all registered exact reference cases and extremal
witnesses, native replay records, correspondence, compact resource/acceptance
receipts and the bulk manifest. Existing Cycle 17 compact checkpoints/ledgers
are reused in place. Native environments, large historical proof exports,
dependency caches and bulk packs remain outside Git.

The [local pack manifest](../../publication/cycle18/manifest.json) lists file and
asset hashes; the [restoration receipt](../../artifacts/cycle18/restoration.json)
records an actual checksum-verified restore. Bulk data stay at
`/home/purplezky/cycle18-evidence-20261117`. There is no release upload, external
artifact hosting, deployment, tag publication or master/main update.

Publication preflight inventories **every new reachable blob across the entire
Cycle 18 commit range**, including superseded versions. Project ceilings are
10 MiB per blob and a target of 100 MiB total new unique content. They are project
budgets, not claims about hosting-platform limits. Secret-pattern checks inspect
both tip files and superseded reachable blobs. Explicit reviewed paths are staged;
the entire working directory is never blindly added.

The actual fetch and push URLs are inspected, including multiple push URLs and
URL rewriting. At registration, origin had one SSH URL for the authorized
repository and only an unrelated dhall-lang rewrite. This is checked again
immediately before pushing. No credential-bearing URLs are printed or committed.
The explicit refspec changes only the dedicated branch:

```bash
git -c push.followTags=false -c push.recurseSubmodules=no \
  push --set-upstream origin HEAD:refs/heads/cycle18-shared-parameter-contract
```

After the final commit, fresh remote queries must match the local SHA through
both origin and the canonical GitHub repository. A fresh canonical checkout must
retrieve the engineering report, architecture decision, reproduction guide and
minimal CLI/source-bound examples at that SHA. The compact contract and native
commands are executed again there with verified reused dependencies and denied
historical/PGN access. Remote-tracking refs alone are insufficient.

The final SHA, full object inventory and publication verification receipt remain
outside the tracked checkout to avoid self-referential commits. The engineering
[acceptance receipt](../../artifacts/cycle18/acceptance.json) binds source,
evidence and reports; it cannot prove a later push. Final publication status is
reported only after the independent remote checks. Already published history is
never rewritten and no force push is used.
