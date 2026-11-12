"""C12-compatible dependency construction with shared durable proof references.

All native expressions and occurrence identities are unchanged. Only host
storage and observation/proof copying differ from the frozen graph builder.
"""
import copy
from pln_chess.common import digest
from pln_chess.pln import TV
from pln_chess.cycle12.ontology import INTERACTIONS
from pln_chess.cycle12.graph import _relation_node, compare_fields


def build_graph(field,concepts=None,*,store,before=None,move=None):
    with store.transaction():
        return _build_graph(field,concepts,store=store,before=before,move=move)


def _build_graph(field,concepts=None,*,store,before=None,move=None):
    concepts=concepts or [];nodes={};edges={};proofs={};snapshots={};tails={}

    def node(identifier,**payload):
        value=dict(id=identifier,**payload)
        if identifier in nodes and nodes[identifier]!=value:raise ValueError('Conflicting graph node identity')
        nodes[identifier]=value;return identifier

    def edge(source,target,predicate,origin,*,truth_value=None,proof_id=None,**provenance):
        value=dict(source=source,target=target,predicate=predicate,origin=origin,truth_value=truth_value,proof_id=proof_id,**provenance)
        value['id']='dependency-edge:'+digest(value);edges[value['id']]=value

    def snapshot(state):
        identifier=state['snapshot_id']
        value={k:state[k] for k in ('fen','pieces','unknown_squares','snapshot_id')}
        if identifier in snapshots and snapshots[identifier]!=value:raise ValueError('Conflicting state identity in graph')
        snapshots[identifier]=value
        node('state:'+identifier,kind='supplied-state',snapshot_id=identifier,truth_value=None)

    snapshot(field)
    if before:snapshot(before)
    for concept in concepts:
        for state in concept['observation']['snapshots'].values():snapshot(state)

    def cell(state_id,square):
        state=snapshots[state_id];unknown={tuple(s) for s in state['unknown_squares']}
        piece=next((p for p in state['pieces'] if tuple(p['square'])==tuple(square)),None)
        observed=tuple(square) not in unknown
        return node('cell:'+digest([state_id,list(square)]),kind='cell-observation',snapshot_id=state_id,square=list(square),
            observed=observed,occupancy='unknown' if not observed else 'occupied' if piece else 'empty',
            piece=copy.deepcopy(piece) if observed else None,truth_value=None)

    def register_proof(record):
        proof_id=record['proof_id'];trace=record['proof_trace']
        if digest(trace)!=proof_id:raise ValueError('Invalid native proof identity')
        reference=store.put(trace)
        if proof_id in proofs and proofs[proof_id]!=reference:raise ValueError('Conflicting native proof')
        proofs[proof_id]=reference;tails[proof_id]=trace[-1]
        return proof_id

    def relation(record):
        observation=record['observation'];state_id=record['snapshot_id'];identifier=_relation_node(state_id,record)
        proposition=node(identifier,kind='native-field-proposition',snapshot_id=state_id,
            relation_id=record['relation_id'],predicate=record['target'],family=record['family'],
            source_entity=record['source_entity'],target_entity=record['target_entity'],source_square=record['source_square'],
            target_square=record['target_square'],relative_displacement=record['relative_displacement'],
            truth_value=record['raw_stv'],truth_value_origin=record['truth_value_origin'],classification=record['classification'],
            model_version=record['model_version'],runtime_version=record['runtime_version'],rule_id=record['rule_id'],
            evidence_ids=record['evidence_ids'],dependence_groups=record['dependence_groups'],proof_id=record['proof_id'],gaps=record['gaps'])
        observed=node(observation['id'],kind='relative-observation',observation=store.put(observation),truth_value=None)
        for dependency in observation['dependencies']:
            source=cell(state_id,dependency['square'])
            predicate='Obstructs' if dependency['role']=='intermediate' and dependency['occupancy']=='occupied' else 'ReadsObservation'
            edge(source,observed,predicate,'host-scheduling',evidence_ids=[observation['id']],dependence_groups=[],
                observation_role=dependency['role'],reads_contents=dependency['occupancy']!='coordinate-only',snapshot_id=state_id)
        edge(observed,proposition,'SchedulesFieldQuery','host-scheduling',evidence_ids=[observation['id']],
            dependence_groups=record['dependence_groups'],rule_ids=[record['rule_id']],model_version=record['model_version'])
        if record['conditional_proof_complete']:
            proof_id=register_proof(record)
            annotation={'attack':'Influences','defense':'Supports','king-exposure':'Exposes','mobility':'Influences','geometry':'Influences'}[record['family']]
            if record['classification']=='contradicted':annotation='RestrictsMobility' if record['family']=='mobility' else 'ContradictsInfluence'
            edge(observed,proposition,record['target'],'native',truth_value=record['raw_stv'],proof_id=proof_id,
                native_predicate=record['target'],interaction_type=annotation,
                interpretation='Interaction type is a host index; this TV belongs to the named native field predicate, not to a newly introduced interaction theorem.',
                evidence_ids=tails[proof_id]['evidence_ids'],dependence_groups=record['dependence_groups'],
                rule_ids=[record['rule_id']],model_version=record['model_version'],runtime_version=record['runtime_version'])
        return proposition,observed

    for state in ([before] if before else [])+[field]:
        for record in state['relations']:relation(record)
    for concept in concepts:
        observation=concept['observation']
        packet=node(observation['id'],kind='host-structural-role-packet',descriptor=observation['descriptor'],roles=observation['roles'],
            complete=observation['complete'],source=observation['source'],truth_value=None,
            scope='Host grouping of observations; no native conjunction of field TVs.')
        conditional=node('concept-conditional:'+digest([observation['id'],concept['model_version'],concept['proof_id'],
            concept['raw_stv'],concept['classification']]),kind='limited-concept-conditional',
            predicate=concept['target'],truth_value=concept['raw_stv'],truth_value_origin=concept['truth_value_origin'],
            classification=concept['classification'],rule_id=concept['rule_id'],model_version=concept['model_version'],
            runtime_version=concept['runtime_version'],proof_id=concept['proof_id'],evidence_ids=concept['evidence_ids'],
            dependence_groups=concept['dependence_groups'])
        candidate=node('concept-candidate:'+digest([concept['case_id'],observation['id'],concept['model_version'],
            concept['proof_id'],concept['classification']]),
            kind='partial-concept-candidate',concept=concept['concept'],case_id=concept['case_id'],
            truth_value=None,joint_proof_complete=False,status=concept['concept_status'],missing_capabilities=concept['missing_capabilities'])
        edge(conditional,candidate,'InterpretsConditional','host-projection',evidence_ids=concept['evidence_ids'],
            dependence_groups=concept['dependence_groups'],joint_proof_complete=False)
        if concept['conditional_proof_complete']:
            proof_id=register_proof(concept)
            edge(packet,conditional,concept['target'],'native',truth_value=concept['raw_stv'],proof_id=proof_id,
                native_predicate=concept['target'],evidence_ids=tails[proof_id]['evidence_ids'],
                dependence_groups=concept['dependence_groups'],rule_ids=[concept['rule_id']],
                model_version=concept['model_version'],runtime_version=concept['runtime_version'])
        else:edge(packet,conditional,'SchedulesConceptQuery','host-scheduling',evidence_ids=[observation['id']],dependence_groups=[])
        for component in concept['field_relations']:
            field_node,observed=relation(component)
            edge(observed,packet,'UpdatesPacketObservation','host-scheduling',evidence_ids=[component['observation_id']],
                dependence_groups=component['dependence_groups'])
            edge(field_node,candidate,'ExplainsConceptRole','host-scheduling',evidence_ids=component['evidence_ids'],
                dependence_groups=component['dependence_groups'],component=component['concept_component'],
                scope='Dependent explanation refresh only. This edge does not propagate or combine a TV.')
    changes=compare_fields(before,field) if before else []
    for change in changes:
        pair=[]
        for side,state in (('before',before),('after',field)):
            record=change[side]
            pair.append(_relation_node(state['snapshot_id'],record) if record else node(
                'absent-domain:'+digest([state['snapshot_id'],change['relation_id']]),kind='absent-domain',
                snapshot_id=state['snapshot_id'],relation_id=change['relation_id'],truth_value=None,
                scope='Outside this observed query domain; not a false proposition.'))
        edge(pair[0],pair[1],change['predicate'],'host-comparison',change_id=change['id'],change_kind=change['change_kind'],
            supplied_move=move,native_temporal_proof=False,
            evidence_ids=sorted({e for side in ('before','after') if change[side] for e in change[side]['evidence_ids']}),
            dependence_groups=sorted({g for side in ('before','after') if change[side] for g in change[side]['dependence_groups']}))
    graph=dict(schema='field-dependency-graph-v12',nodes=[nodes[k] for k in sorted(nodes)],edges=[edges[k] for k in sorted(edges)],
        proofs={k:proofs[k] for k in sorted(proofs)},snapshots=snapshots,changes=changes,
        interaction_signatures=INTERACTIONS,joint_proof_complete=False,automatic_truth_value_propagation=False,
        scope='Native proof index plus explicit host scheduling, grouping and comparisons. Shared evidence remains shared.')
    graph['id']='dependency-graph:'+store.legacy_digest(store.put(graph))
    validate_compact_graph(graph,tails)
    return graph


def validate_compact_graph(graph,tails):
    nodes={n['id']:n for n in graph['nodes']}
    if len(nodes)!=len(graph['nodes']) or graph['automatic_truth_value_propagation'] or graph['joint_proof_complete']:
        raise ValueError('Invalid compact dependency graph')
    for edge in graph['edges']:
        if edge['source'] not in nodes or edge['target'] not in nodes:
            raise ValueError('Dangling compact graph dependency')
        if edge['origin']=='native':
            TV.from_json(edge['truth_value']);tail=tails.get(edge['proof_id'])
            if tail is None or edge['truth_value']!=tail['truth_value'] or edge['native_predicate']!=tail['conclusion']['predicate']:
                raise ValueError('Native conclusion mismatch')
            if edge['model_version']!=tail['model_version'] or edge['runtime_version']!=tail['runtime_version']:
                raise ValueError('Native provenance mismatch')
        elif edge['origin'] not in ('host-scheduling','host-comparison','host-projection') or edge['truth_value'] is not None or edge['proof_id'] is not None:
            raise ValueError('Host graph edge cannot introduce a native truth value')
        if edge['id']!='dependency-edge:'+digest({k:v for k,v in edge.items() if k!='id'}):
            raise ValueError('Invalid dependency edge identity')
    return True
