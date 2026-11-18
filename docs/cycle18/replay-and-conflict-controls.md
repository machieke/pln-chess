# Learning, application and replay controls

The [executed control receipt](../../artifacts/cycle18/contract/controls/results.json)
starts from an actual admitted S-AA evaluation vector and its environmental
parent. All new measurements, corruptions and corrections stay in a separate
in-memory research registry. Original training ledgers and checkpoints are never
written. The tests cover behavior and mathematical consequences rather than just
serialization shape.

| Control | Executed result |
| --- | --- |
| Same event delivered ten additional times | Zero additions; unchanged registry, posterior and generation |
| Same payload, different event and source | Both retained; supplied across-group independence permits a new likelihood; dependence is not inferred from IDs |
| Same ID, changed payload | Rejected without changing the registry |
| Explicit new superseding version | Old immutable record retained; old active update rejected; competing successors rejected |
| Two actual annotation aliases | One vector likelihood under copy semantics, not two local likelihoods |
| Applications repeated 1, 10, 100 times | Only journal length changes; event set, posterior, bounds and generation identity stay fixed |
| New synthetic external observation | New event set, generation lineage and posterior |
| Remove one actual source group | Full recomputation from eleven source vectors; no confidence subtraction |
| Incremental ingestion and reversed ordering | Each prefix equals complete reconstruction; final result exactly equals batch fit |
| Shared-ancestor diamond | Both branches reference the same generation/event identity; joining does not relearn |
| Ten cyclic query revisits without observations | Zero evidence additions and unchanged posterior |
| Different state or history | Different contextual identity, preventing stale context reuse |
| Prediction/application offered as observation | Type/origin rejection; unapproved self-training prohibited |
| Unknown label or excluded/derived annotation offered for fitting | Rejected; no unknown-to-false conversion |
| Two distinct measurements in one source group | Rejected until a joint within-group likelihood is supplied |
| Missing dependence | Explicit bounds under named fixed marginals, otherwise not identified |
| State/group/evaluation/rational limits | Four deliberate `resource_incomplete` results without predictions |

The application journal is a bounded sequence of uses, not a new inference
engine or a proof-graph solver. Diamond/cycle links are explicitly declared host
application ancestry. The unchanged native runtime's actual diamond/cycle
controls are separate and preserved in the
[native replay](../../artifacts/cycle18/native/summary.json). There is no claim
that the journal solves native recursion.
Application sequence IDs are local to their journal/output generation; they are
not external observation IDs or claims of globally independent events.

The noise-free copy model gives zero likelihood to a vector with disagreeing
labels. The corrupt vector is an explicit synthetic alteration of a real source
example. It returns `inconsistent_evidence`; no zero division, epsilon, overwrite
or silent noise repair occurs. The supersession control adds an explicitly
identified corrected version; it does not edit the historical example.

Three declared two-measurement models make the distinction concrete. A fair
latent binary value is read twice. With readings (true,true), noiseless copies
give posterior latent-true probability 1; a **shared** bit-flip noise event with
probability 1/10 gives 9/10; independent bit flips of probability 1/10 give
81/82. With disagreeing readings, the first two models are inconsistent, while
independent flips produce probability 1/2. Complete unnormalized weights and
normalization statuses are retained. These synthetic noise assumptions were
registered beforehand; no noise rate was estimated from TCEC labels.

An application is not a measurement. Recomputing a parameter from the same active
events is not a new observation. Updating with a new external event, correcting
an event through explicit supersession, and selecting another model's assumptions
are distinct operations with distinct identities. These contracts demonstrate
replay safety within this bounded reference laboratory; they do not establish
a replacement native uncertainty policy.
