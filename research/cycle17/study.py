"""Native two-stage requests. No evaluation or reference-mathematics imports."""
from dataclasses import asdict
from pathlib import Path
from pln_chess.common import digest, read_json
from research.cycle15.native_reasoner import NativeReasoner
from research.cycle16.experiments import observations, knowledge, MEDIUM, SEMANTICS, support_status


def infer(state, attacker, target, *, checkpoint=None, arm='F', budgets=None,
          remove=(), facts_transform=None, full_scope=False, reasoner=None):
    facts, scope = observations(state, attacker, target, full_scope=full_scope)
    if facts_transform is not None:
        facts = facts_transform(facts)
    rules = [r for r in knowledge('L' if checkpoint else arm, checkpoint) if r.stamps[0][5:] not in remove]
    reasoner = reasoner or NativeReasoner()
    state_id = state['id']; shape = scope['shape'] or 'unaligned'
    queries = {'Clear': (f'(Clear {attacker} {target} {shape} {state_id})', None),
        'Attack': (f'(Attack {attacker} {target} {state_id})', f'(NoAttack {attacker} {target} {state_id})')}
    stages = {}
    for name, (query, contrary) in queries.items():
        result = reasoner.infer(facts, rules, query, contrary=contrary, budgets=budgets or MEDIUM)
        result['support_status'] = support_status(result)
        stages[name] = result
    if isinstance(checkpoint, (str, Path)):
        checkpoint = read_json(checkpoint)
    return dict(target_semantics=SEMANTICS, observation_scope=scope, stages=stages,
        query_domain_valid=scope['attacker_present'] and scope['target_present'],
        checkpoint_identity=checkpoint['version'] if checkpoint else None,
        knowledge_identity=digest([r.metta() for r in rules]), raw_observations=[asdict(f) for f in facts],
        inference_boundary='Fresh native calls from raw observations and whole rule set; no staged answers')
