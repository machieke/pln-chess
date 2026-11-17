"""Post-hoc diagnostics only. No diagnostic supplies an inference answer."""
from pln_chess.common import digest
from research.cycle15.native_reasoner import alpha_key, parse
from research.cycle16.evidence_audit import pair_diagnostic


def witness(result, out):
    attack = result['stages']['Attack']
    _, a, t, s = parse(attack['query'])
    clear_term = f'(Clear {a} {t} orthogonal {s})'
    partial_term = f'(Implication (Clear {a} $target orthogonal {s}) (Attack {a} $target {s}))'
    clears = [r for r in attack['retained'] if r['term'] == clear_term]
    partials = [r for r in attack['retained'] if alpha_key(r['term']) == alpha_key(partial_term)]
    causes = []
    diagnostic = None
    if clears and partials:
        clear = max(clears, key=lambda r: r['confidence'])
        partial = max(partials, key=lambda r: r['confidence'])
        diagnostic = pair_diagnostic(partial, clear, out)
        for prefix, category in [('train_', 'shared training ancestry'), ('rule_', 'shared rule identity'), ('obs_', 'shared environmental evidence')]:
            if any(stamp.startswith(prefix) for stamp in diagnostic['overlap']):
                causes.append(category)
    else:
        causes.append('missing statement')
    if attack['incomplete']:
        causes.append('timeout or malformed execution')
    if attack['classification'] == 'unknown' and attack['answer']:
        causes.append('confidence or strength below threshold')
    if attack['remaining']:
        causes.append('remaining tasks; completeness unestablished')
    if not result['query_domain_valid']:
        causes.append('unsupported query domain')
    return dict(diagnostic=diagnostic, causes=causes, clearance_present=bool(clears), terminal_partial_present=bool(partials),
        native_classification=attack['classification'], native_answer=attack['answer'],
        scope='Returned statements revalidated by native operator/guard; scheduler pair attempt not observable')


def roles(result, model):
    """Trace identities describe outputs; parents remain unknown when unexposed."""
    from .corpus import roots
    rules = model.get('rules', {}) if model else {}
    observations = {r['source_ancestry']: digest([r['state'], r['attacker'], r['target']]) for r in roots()}
    mapped = [dict(schema_id=r['stamps'][0],
        parameter_generation_id=digest(rules[r['stamps'][0][5:]]) if r['stamps'][0][5:] in rules else 'supplied-confidence-0.95',
        training_observation_ids=[observations[g] for g in r['ancestry']],
        training_evidence_record_ids=rules.get(r['stamps'][0][5:], {}).get('evidence', []),
        training_ancestry_groups=r['ancestry'], environmental_observation_ids=[],
        application_id=None, parent_derivations=None, native_stamps=r['stamps'],
        scope='Input provenance mapping; application and fired-rule parents not exposed')
        for r in result['stages']['Attack']['rules']]
    environment = [dict(schema_id=None, parameter_generation_id=None,
        training_observation_ids=[], training_ancestry_groups=[],
        environmental_observation_ids=f['stamps'], application_id=None, parent_derivations=None,
        native_stamps=f['stamps'], source_ancestry=f['ancestry'], term=f['term'])
        for f in result['stages']['Attack']['facts']]
    trace = [dict(application_id='selected_'+str(i), parent_derivations=None,
        native_stamps=s['stamps'], term=s['term'],
        scope='Observed selection identity, not a firing or independent evidence')
        for i, s in enumerate(result['stages']['Attack']['selected'])]
    return dict(rules=mapped, environment=environment, selections=trace)


def failure_census(result):
    """Inventory missing support without inventing scheduler rejection events."""
    census = {}
    for name, stage in result['stages'].items():
        if stage['classification'] not in ('unknown', 'incomplete', 'conflicting'):
            continue
        causes = []
        if stage['incomplete']:
            causes.append('timeout or malformed execution')
        elif stage['classification'] == 'conflicting':
            causes.append('both channels supported')
        elif stage['answer'] or stage['contrary']:
            causes.append('below display threshold')
        if not result['query_domain_valid']:
            causes.append('unsupported query domain')
        if sum(f['term'].startswith('(Empty ') for f in stage['facts']) < 2:
            causes.append('missing required emptiness premise')
        if stage['remaining']:
            causes.append('remaining tasks; no completeness claim')
        if name == 'Attack':
            _, a, t, s = parse(stage['query'])
            partial = alpha_key(f'(Implication (Clear {a} $target orthogonal {s}) (Attack {a} $target {s}))')
            clears = [r for r in stage['retained'] if r['term'] == f'(Clear {a} {t} orthogonal {s})']
            terminals = [r for r in stage['retained'] if alpha_key(r['term']) == partial]
            if clears and terminals:
                overlaps = [set(c['stamps']) & set(p['stamps']) for c in clears for p in terminals]
                if all(overlaps):
                    causes.append('returned matching pair has overlapping stamps; native guard checked in minimal witness')
            else:
                causes.append('clearance or terminal partial absent')
        census[name] = causes or ['no supported answer returned within budget']
    return census


def audit(result):
    counts = dict(statements=0, channels=0)
    for stage in result['stages'].values():
        allowed = {s for r in stage['facts']+stage['rules'] for s in r['stamps']}
        for group in ('selected', 'retained', 'remaining'):
            for statement in stage[group]:
                assert statement['stamps'] and set(statement['stamps']) <= allowed
                counts['statements'] += 1
        for key in ('answer', 'contrary'):
            if stage[key]:
                assert set(stage[key]['stamps']) <= allowed
                counts['channels'] += 1
    return counts
