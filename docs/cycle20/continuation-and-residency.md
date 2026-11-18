# Continuation and same-process residency

| Workspace | Matched schedules | Selected | Final tasks | Retained | Exact comparison |
|---|---|---:|---:|---:|---|
| Two crossing rays | 64 versus 16 + 16 + 32 | 64 | 11 | 75 | Concatenated selected sequence, both raw queues, completion and every readout |
| Eight constructed rays | 96 versus 32 + 64 | 96 | 55 | 151 | Same checks, including non-ground partial conditionals |

PLN.Derive starts its step counter at one per invocation and stops after the chunk allowance or on an empty task queue. Each chunk receives the previous returned task and belief tuples with capacities fixed. Intermediate readouts and disk restoration preserved the raw queues. Equal-priority selection, zero extra steps, exhausted queues, near-capacity removal and rejection of an interrupted child passed. [Schedules and parent references](../../artifacts/cycle20/witnesses/continuation.json) · [Uninterrupted native output](../../artifacts/cycle20/witnesses/chunk-1-uninterrupted.json) · [Last chunk](../../artifacts/cycle20/witnesses/chunk-1-last_chunk.json)

The live research session uses private pipes to one SWI process. It loads the pinned PeTTa library and calls its existing process_metta_string interface. PeTTa change-state! stores the tuple inside the runtime. A later request uses get-state with the original native selector. The framing layer handles request IDs, generation checks, timeouts and shutdown. [Host interface](../../research/cycle20/resident.py) · [Frame loop](../../research/cycle20/frames.pl)

The resident witness loaded one query in PID 1376191. Only after that response did the host request the previously unrequested State proposition. Request sizes were 17,560, 248 and 1,660 bytes for load, later selection and continuation respectively. The later request returned the matching observation stamp with zero derivation markers and zero selected tasks. Its native answer matched fresh serialized selection. A 48-step continuation in the same PID matched uninterrupted execution. Old-generation and closed-session operations were rejected. The private session is bounded to one owning host and one generation lineage. [Complete native wire witness](../../artifacts/cycle20/witnesses/residency.json)

Before benchmarking, the capability investigation opened three sessions, each receiving three host programs. Two verification runs also executed four separate file-runner references in total. That gives 13 focused programs, or 16 when the three pinned-library loads are counted separately, within the registered ceiling of 24. Later timing and published-checkout runs are accounted for independently.
