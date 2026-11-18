# Capacity and paired performance

The serial paired benchmark used seven repetitions per mode on the same two-ray D-AB fixture, machine, runtime, step allowance and capacities. Comparator order alternated between repetitions. The full comparison matrix and capability runs finished before timing. Historical preservation started afterward. Aggregate wall time includes host preparation, native execution, parsing and the mode's requested readouts. CPU includes host and reaped child CPU. Per-process peak memory uses GNU time where available. Resident frame timing measures the already-open process separately.

| Mode | Wall median s | Wall range s | CPU median s | Starts | Derivations | Native readouts |
|---|---:|---:|---:|---:|---:|---:|
| chunked | 5.5992 | 5.4960–5.7664 | 5.4995 | 2 | 2 | 12 |
| combined-batch | 1.8315 | 1.8154–1.9168 | 1.7893 | 1 | 1 | 6 |
| combined-separate | 7.2386 | 7.1829–7.4044 | 7.0806 | 4 | 4 | 6 |
| corrected-rebuild | 1.9538 | 1.8783–1.9772 | 1.8962 | 1 | 1 | 6 |
| host-cache | 0.0002 | 0.0002–0.0004 | 0.0002 | 0 | 0 | 0 |
| legacy-separate | 4.8164 | 4.6122–5.0717 | 4.6176 | 4 | 4 | 6 |
| local-batch | 2.4822 | 2.4582–2.6100 | 2.4030 | 2 | 2 | 6 |
| resident-load-read-continue | 0.9244 | 0.8888–1.0782 | 0.9187 | 1 | 2 | 8 |
| restored-read | 4.2327 | 4.1204–4.3778 | 4.1644 | 1 | 0 | 6 |

The median warm resident read took 0.00121 s. The cache sample served an already established result from host memory. Startup, restoration and correction rebuilds have different work totals. The sample size supports medians and observed ranges only. [Raw samples](../../artifacts/cycle20/benchmark/raw-samples.json) · [Summary](../../artifacts/cycle20/benchmark/summary.json)

| Loaded rays | Workspaces | Unique input facts | Selected | Remaining | Retained records | Unique retained propositions |
|---:|---:|---|---|---|---|---|
| 1 | 30 | [19, 25] | [45, 53] | [0, 0] | [45, 53] | [45, 52] |
| 2 | 30 | [31, 44] | [64, 64] | [4, 23] | [68, 87] | [68, 87] |
| 3 | 3 | [55, 55] | [64, 64] | [45, 46] | [109, 110] | [109, 110] |
| 4 | 24 | [49, 78] | [64, 64] | [29, 84] | [93, 148] | [93, 148] |
| 5 | 9 | [84, 97] | [64, 64] | [77, 88] | [141, 152] | [141, 152] |
| 6 | 6 | [109, 109] | [64, 64] | [85, 114] | [149, 178] | [149, 178] |
| 8 | 3 | [85, 85] | [64, 64] | [71, 71] | [135, 135] | [135, 135] |

Each bracketed pair is the observed minimum and maximum for that size. Native rules, observation records, source stamps, alternatives sharing a proposition, repeated readouts and semantic targets are counted separately in the detailed table. The combined runs used one process and one top-level derivation per admitted workspace. Within each ray, Clear is one target and Attack is a second target with two readouts. The pinned selector scans the retained tuple for each requested term. All observed resource, coverage and timing measurements are restricted to this bounded panel. [Capacity detail](../../artifacts/cycle20/capacity.json) · [Per-run measurements](../../artifacts/cycle20/combined-workloads.json)

Fresh limits enforce at most 256 tasks and 256 sentences. Registered native queues allow up to 512. The 257-fresh-record control returned a resource refusal with no semantic answers. A real native return of 259 sentences restored correctly. An intentionally interrupted continuation failed without publishing partial state. During development, an unnamespaced test stamp collided with PeTTa's first operator and was rejected by the output decoder. Fresh and restored inputs now enforce namespaced evidence IDs. An initial regression test picked a learning receipt from a mixed proof directory. The corrected test follows the registered positive demonstration's Attack receipt. [Control results](../../artifacts/cycle20/witnesses/controls.json) · [Research accounting](../../artifacts/cycle20/accounting.json)

File-runner timings include the metered raw receipt write for each process. Resident frame capture is in memory during timing and its sample file is written afterward. Comparisons across transports include these accounting differences. Resident frame measurements include the SWI process memory high-water mark. The two-chunk benchmark repeats six native readout terms at its second boundary. Resident load and continuation repeat one term. The late State read is a separate observational readout in addition to the four chess targets. [Measured resident frames](../../artifacts/cycle20/benchmark/resident-frames-sample.json)
