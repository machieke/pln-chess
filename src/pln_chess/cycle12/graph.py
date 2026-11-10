"""Typed proof indexes and host dependency edges, without TV propagation."""
import copy
from pln_chess.common import digest
from pln_chess.pln import TV
from .ontology import INTERACTIONS


def _endpoint(record):
    if record is None:return None
    return {key:record[key] for key in ('relation_id','family','source_entity','target_entity','source_square','target_square',
        'relative_displacement','classification','raw_stv','rule_id','proof_id','evidence_ids','dependence_groups',
        'observation_id','model_version','runtime_version','gaps','conditional_proof_complete')}


def _relation_node(snapshot,record):
    # A proposition can have distinct source observations or checkpoint proofs.
    # They must coexist instead of overwriting one another's provenance.
    return 'field:'+digest([snapshot,record['relation_id'],record['observation_id'],record['model_version'],
        record['runtime_version'],record['proof_id'],record['raw_stv'],record['classification'],record['gaps']])


def compare_fields(before,after,*,include_persistence=True):
    first={r['relation_id']:r for r in before['relations']};second={r['relation_id']:r for r in after['relations']}
    changes=[]
    compared=('classification','raw_stv','rule_id','proof_id','evidence_ids','dependence_groups','observation_id',
              'source_square','target_square','relative_displacement')
    for identifier in sorted(first.keys()|second.keys()):
        a,b=first.get(identifier),second.get(identifier);family=(a or b)['family']
        unchanged=a is not None and b is not None and all(a[k]==b[k] for k in compared)
        if unchanged and not include_persistence:continue
        predicate='ChangesInfluence'
        if unchanged:predicate='PersistsAcrossMove';kind='unchanged-'+a['classification']
        elif a is None:kind='domain-created'
        elif b is None:
            kind='domain-removed'
            if family=='defense' and a['classification']=='supported':predicate='RemovesDefense'
        elif family=='attack' and a['classification']=='contradicted' and b['classification']=='supported':
            predicate='OpensAttack';kind='counterevidence-to-support'
        elif family=='defense' and a['classification']=='supported' and b['classification']=='contradicted':
            predicate='RemovesDefense';kind='support-to-counterevidence'
        elif a['classification']!=b['classification']:kind='classification-changed'
        elif b['raw_stv']['strength']>a['raw_stv']['strength']:kind='strengthened'
        elif b['raw_stv']['strength']<a['raw_stv']['strength']:kind='weakened'
        elif b['raw_stv']['confidence']>a['raw_stv']['confidence']:kind='confidence-increased'
        elif b['raw_stv']['confidence']<a['raw_stv']['confidence']:kind='confidence-decreased'
        else:kind='observation-evidence-or-dependency-changed'
        change=dict(relation_id=identifier,family=family,predicate=predicate,change_kind=kind,
            before=_endpoint(a),after=_endpoint(b),before_snapshot=before['snapshot_id'],after_snapshot=after['snapshot_id'],
            truth_value=None,origin='host-comparison',native_temporal_proof=False,
            support_persists=bool(a and b and a['classification']==b['classification']=='supported'),
            interpretation='Comparison of separately supported endpoint records. Unknown or absent is not false; persistence is not new independent evidence.')
        change['id']='field-change:'+digest(change);changes.append(change)
    return changes


def compare_concepts(before,after):
    """Compare like role bindings without turning absent enumeration into falsity."""
    def identity(record):
        return digest([record['concept'],[(name,fact['piece']['id'] if fact['piece'] else ['cell',fact['square']])
            for name,fact in sorted(record['observation']['roles'].items())]])
    first={identity(c):c for c in before};second={identity(c):c for c in after};result=[]
    def endpoint(c):
        return None if c is None else {k:c[k] for k in ('case_id','concept','target','classification','raw_stv',
            'proof_id','rule_id','observation_id','evidence_ids','dependence_groups','model_version','missing_capabilities')}
    for identifier in sorted(first.keys()|second.keys()):
        a,b=first.get(identifier),second.get(identifier)
        result.append(dict(role_binding_id=identifier,before=endpoint(a),after=endpoint(b),
            change_kind='enumeration-created' if a is None else 'enumeration-removed' if b is None else
                'conditional-persisted' if a['raw_stv']==b['raw_stv'] and a['classification']==b['classification'] else 'conditional-changed',
            truth_value=None,origin='host-comparison',native_temporal_proof=False,
            scope='Separate role-bound endpoint conditionals. Enumeration absence is not a negative concept conclusion.'))
    return result


def build_graph(field,concepts=None,*,before=None,move=None):
    concepts=concepts or [];nodes={};edges={};proofs={};snapshots={}

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
        if proof_id in proofs and proofs[proof_id]!=trace:raise ValueError('Conflicting native proof')
        proofs[proof_id]=copy.deepcopy(trace)
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
        observed=node(observation['id'],kind='relative-observation',observation=copy.deepcopy(observation),truth_value=None)
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
                evidence_ids=proofs[proof_id][-1]['evidence_ids'],dependence_groups=record['dependence_groups'],
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
                native_predicate=concept['target'],evidence_ids=proofs[proof_id][-1]['evidence_ids'],
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
    graph['id']='dependency-graph:'+digest(graph)
    validate_graph(graph)
    return graph


def validate_graph(graph):
    nodes={n['id']:n for n in graph['nodes']}
    if len(nodes)!=len(graph['nodes']) or graph.get('automatic_truth_value_propagation') is not False or graph.get('joint_proof_complete') is not False:
        raise ValueError('Invalid graph identity or unsupported composition claim')
    for identifier,trace in graph['proofs'].items():
        if not trace or digest(trace)!=identifier:raise ValueError('Unbound graph proof')
    for edge in graph['edges']:
        if edge['source'] not in nodes or edge['target'] not in nodes:raise ValueError('Dangling graph dependency')
        if edge['origin']=='native':
            TV.from_json(edge['truth_value']);trace=graph['proofs'].get(edge['proof_id'])
            if not trace or edge['truth_value']!=trace[-1]['truth_value'] or edge['native_predicate']!=trace[-1]['conclusion']['predicate']:
                raise ValueError('Graph edge does not match its native conclusion')
            if edge['model_version']!=trace[-1]['model_version'] or edge['runtime_version']!=trace[-1]['runtime_version']:
                raise ValueError('Graph/native provenance mismatch')
        elif edge['origin'] not in ('host-scheduling','host-comparison','host-projection') or edge['truth_value'] is not None or edge['proof_id'] is not None:
            raise ValueError('Host dependency edges cannot introduce native truth values')
        if edge['id']!='dependency-edge:'+digest({k:v for k,v in edge.items() if k!='id'}):raise ValueError('Invalid edge identity')
    if graph['id']!='dependency-graph:'+digest({k:v for k,v in graph.items() if k!='id'}):raise ValueError('Invalid graph identity')
    return True
