# Matched performance measurements

Four frozen workloads compare legacy full responses and compact summaries with the same C13 checkpoints, native evidence and inputs. Each arm has **20 repetitions**, in fresh processes, with cold and warm requests. All 320 measured request groups have exact native/evidence parity. Workloads cover one quiet pair, three mixed pairs including promotion/tactical cases, two supplied plies and three supplied plies. Alternating arm order reduces ordering bias.

| Workload | Arm | Temperature | Median interactive seconds | Median inference seconds | Interactive bytes | Compressed audit bytes | Parent peak KiB | Interpreter launches |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single | legacy | cold | 7.617264 | 7.217208 | 54120364 | 2750856 | 274238 | 8.0 |
| single | legacy | warm | 4.516471 | 4.121149 | 54120363 | 2750804 | 316166 | 0.0 |
| single | compact | cold | 12.780386 | 12.780242 | 6147 | 4546036 | 262260 | 8.0 |
| single | compact | warm | 0.089810 | 0.089754 | 6146 | 4546036 | 275706 | 0.0 |
| multiple | legacy | cold | 19.911384 | 18.807364 | 144737705 | 7190194 | 468966 | 17.0 |
| multiple | legacy | warm | 14.723777 | 13.618561 | 144737720 | 7190130 | 513880 | 4.0 |
| multiple | compact | cold | 23.323021 | 23.322865 | 17904 | 12343536 | 279050 | 15.0 |
| multiple | compact | warm | 0.260617 | 0.260461 | 17903 | 12343536 | 280528 | 0.0 |
| two-ply | legacy | cold | 15.164310 | 14.077060 | 146046818 | 7460096 | 615014 | 15.0 |
| two-ply | legacy | warm | 11.757818 | 10.685926 | 146046819 | 7459980 | 719320 | 6.0 |
| two-ply | compact | cold | 23.087833 | 23.087641 | 14029 | 6816014 | 351388 | 15.0 |
| two-ply | compact | warm | 0.073944 | 0.073832 | 14029 | 6816014 | 357022 | 0.0 |
| three-ply | legacy | cold | 20.797346 | 19.399987 | 182767790 | 9292144 | 756322 | 21.0 |
| three-ply | legacy | warm | 16.428223 | 15.022681 | 182767799 | 9292012 | 890140 | 10.0 |
| three-ply | compact | cold | 32.142173 | 32.141963 | 15966 | 9167942 | 448434 | 21.0 |
| three-ply | compact | warm | 0.071415 | 0.071288 | 15965 | 9167942 | 459032 | 0.0 |

| Workload | Temperature | Median paired legacy/compact latency | 95% median-ratio interval | Interactive payload reduction |
| --- | --- | --- | --- | --- |
| single | cold | 0.60× | 0.59–0.60× | 99.9886% |
| single | warm | 49.89× | 49.60–50.56× | 99.9886% |
| multiple | cold | 0.85× | 0.85–0.86× | 99.9876% |
| multiple | warm | 56.04× | 55.14–56.84× | 99.9876% |
| two-ply | cold | 0.65× | 0.65–0.66× | 99.9904% |
| two-ply | warm | 167.32× | 153.87–172.18× | 99.9904% |
| three-ply | cold | 0.65× | 0.64–0.65× | 99.9913% |
| three-ply | warm | 229.88× | 213.44–234.52× | 99.9913% |

Using the observed median paired ratios, **4/4 workloads meet the twofold warm-summary latency target** and **4/4 meet the 90% interactive-payload reduction target at both cold and warm requests**. The [target assessment](../../artifacts/cycle14/delivery/performance-goals.json) records each workload. These are measurements of the frozen workloads, not guarantees for arbitrary requests or complete-audit execution.

Cold compact requests take longer in 4/4 workloads: the compact/legacy median paired latency ratios range from 1.17 to 1.68. Complete-audit work takes 2.67–4.93 times the legacy median time, and compressed audit archives are 0.91–1.72 times the legacy median size. These audit and archive ratios divide the displayed arm medians. The compact summary gains carry measurable cold-request and audit costs.

Complete-audit costs and interactive tail samples are separate measurements. The benchmark requests 64 proof objects per page. All time columns below are seconds; audit, retrieval, byte and RSS values are medians over twenty runs.

| Workload | Arm | Temperature | Reconstructed full bytes | Audit validation + compression seconds | Graph page seconds | Interactive p95 seconds | Interactive sample p99 seconds | Largest child peak KiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single | legacy | cold | 54120362 | 2.475031 | not applicable | 7.794063 | 7.833404 | 105388 |
| single | legacy | warm | 54120361 | 2.827849 | not applicable | 4.602205 | 4.604516 | 105388 |
| single | compact | cold | 54120363 | 12.212128 | 1.253962 | 12.984717 | 12.996138 | 101792 |
| single | compact | warm | 54120363 | 12.339978 | 1.233166 | 0.102216 | 0.149086 | 101792 |
| multiple | legacy | cold | 144737701 | 6.990671 | not applicable | 20.109147 | 20.211178 | 145284 |
| multiple | legacy | warm | 144737716 | 7.124611 | not applicable | 14.910183 | 15.067711 | 468966 |
| multiple | compact | cold | 144737700 | 33.821500 | 3.474017 | 23.499947 | 23.533094 | 106234 |
| multiple | compact | warm | 144737700 | 34.251742 | 3.481922 | 0.276625 | 0.310186 | 106234 |
| two-ply | legacy | cold | 146046816 | 6.861751 | not applicable | 16.419155 | 16.611561 | 159206 |
| two-ply | legacy | warm | 146046817 | 7.189304 | not applicable | 13.313993 | 13.572054 | 615014 |
| two-ply | compact | cold | 146046817 | 19.173854 | 1.913881 | 24.435751 | 25.175825 | 111146 |
| two-ply | compact | warm | 146046817 | 19.208786 | 1.938583 | 0.112782 | 0.115963 | 111146 |
| three-ply | legacy | cold | 182767788 | 8.866210 | not applicable | 21.744552 | 21.780896 | 195624 |
| three-ply | legacy | warm | 182767797 | 9.021252 | not applicable | 17.836343 | 19.916680 | 756322 |
| three-ply | compact | cold | 182767785 | 25.949129 | 2.420618 | 33.762551 | 36.748686 | 119334 |
| three-ply | compact | warm | 182767785 | 26.349608 | 2.435235 | 0.089658 | 0.091357 | 119334 |

| Workload | Arm | Fresh processes | Median runtime load seconds | Median model load seconds |
| --- | --- | --- | --- | --- |
| multiple | legacy | 20 | 0.006216 | 0.421616 |
| multiple | compact | 20 | 0.006250 | 0.421036 |
| single | legacy | 20 | 0.006327 | 0.420940 |
| single | compact | 20 | 0.006254 | 0.418539 |
| three-ply | legacy | 20 | 0.006256 | 0.429794 |
| three-ply | compact | 20 | 0.006268 | 0.428076 |
| two-ply | legacy | 20 | 0.006254 | 0.429065 |
| two-ply | compact | 20 | 0.006272 | 0.423613 |

Interactive latency includes inference and canonical serialization. Model/runtime loading is measured separately and excluded symmetrically. Compact warm requests reuse a durable request bound to source, state, history, models, runtime, branches and options. This avoids repeated work; it is not a native interpreter speedup. Cold construction, complete archive validation/compression and graph-page retrieval have separate distributions in the [benchmark receipt](../../artifacts/cycle14/performance/summary.json). Returning less data is an interface improvement, not proof that complete-audit execution became equally fast.

Parent peak RSS is measured in a fresh process per workload/arm/repetition and includes audit validation/export. Warm RSS retains the prior cold peak and caches. Child maximum RSS is reported separately and never added to parent lifetime maxima as a fictitious simultaneous working set. Twenty-observation p99 is a sample statistic, not a service guarantee. Median uncertainty uses 1,000 bootstrap samples.

The [pre-optimization profile](../../artifacts/cycle14/profile-before/profile.json) and storage profiles are instrumented diagnostics under concurrent work. Their cumulative times overlap and cannot supply headline speed ratios. The isolated benchmark rejects concurrent owned study/native workers; unrelated host load remains uncontrolled and is disclosed. No browser transfer/rendering latency guarantee is inferred from functional screenshots.

Per-request data-access records distinguish persistent learned checkpoint hypotheses, host relation/cache entries, grounded proposition occurrences, derived proof nodes, stored proof objects and invalidations. Persistent native-resident atoms are zero. A reused summary retains its original proof census while recording zero newly materialized grounding. The host Merkle index is not a persistent native reasoning graph.
