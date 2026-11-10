"""Native local conditionals and exact dependency-bound field reuse."""
import copy
from dataclasses import dataclass, asdict
import math
import time

from pln_chess.common import canonical, digest
from pln_chess.domain import Position, parse_square, square_name
from pln_chess.inference import Options, classify
from pln_chess.pln import Runtime, TV, UNKNOWN, NativeError
from pln_chess.cycle3.native import NativeSession
from .ontology import FIELDS, TARGETS, observe_relation, validate_position, snapshot_id


@dataclass(frozen=True)
class FieldOptions(Options):
    max_native_invocations: int = 100000
    timeout_seconds: float = 180
    sensor_confidence: float = .99

    def __post_init__(self):
        super().__post_init__()
        if type(self.max_native_invocations) is not int or not math.isfinite(self.timeout_seconds):
            raise ValueError('Field budgets require a finite timeout and integer proof-node limit')
        if isinstance(self.sensor_confidence,bool) or not math.isfinite(self.sensor_confidence) or not 0<=self.sensor_confidence<1:
            raise ValueError('Field sensor confidence must be finite and in [0,1)')
        if any(not math.isfinite(v) for v in (self.min_confidence,self.supported_strength,self.contradicted_strength)):
            raise ValueError('Field classification thresholds must be finite')


class FieldSession:
    def __init__(self,runtime,optimized=True,max_entries=20000):
        if type(max_entries) is not int or max_entries<0:
            raise ValueError('Invalid relation-cache capacity')
        self.runtime=runtime
        self.optimized=optimized
        self.max_entries=max_entries
        self.native=NativeSession(runtime,optimized=optimized)
        self.scope=None
        self.relations={}
        self.invalidations=0

    def bind(self,scope):
        if scope!=self.scope:
            self.invalidations+=len(self.relations)
            self.relations.clear()
            self.scope=scope
        self.native.bind(scope)

    def get(self,identifier,fingerprint):
        if not self.optimized or identifier not in self.relations:
            return None
        previous,record=self.relations[identifier]
        if previous!=fingerprint:
            self.invalidations+=1
            del self.relations[identifier]
            return None
        return record

    def put(self,identifier,fingerprint,record):
        if self.optimized and self.max_entries:
            self.relations[identifier]=(fingerprint,record)
            while len(self.relations)>self.max_entries:
                self.relations.pop(next(iter(self.relations)))


def _record(observation,hypothesis,model_version,runtime_version):
    return dict(relation_id=observation['relation_id'],family=observation['family'],target=observation['target'],
        source_entity=observation['source_entity'],source_square=observation['source_square'],
        target_square=observation['target_square'],target_entity=observation['target_entity'],
        relative_displacement=observation['relative_displacement'],rule_id=observation['rule_id'],
        descriptor=observation['descriptor'],observation=observation,observation_id=observation['id'],
        evidence_ids=list(hypothesis['evidence_ids']) if hypothesis else [],
        dependence_groups=list(hypothesis['dependence_groups']) if hypothesis else [],
        model_version=model_version,runtime_version=runtime_version,
        raw_stv=UNKNOWN.json(),truth_value_origin='absence-prior',classification='unknown',
        conditional_proof_complete=False,global_composition_complete=False,
        proof_trace=[],proof_id=digest([]),proof_status='no-native-conditional-proof',gaps=list(observation['gaps']),
        interpretation='Local conditional influence only; legal recapture, global safety, strategic value and a joint uncertain-premise theorem are not established.')


def _schedule(observation,hypothesis,model_version,runtime_version,sensor):
    stem='field'+observation['id'].split(':')[1][:32]
    names=[stem+suffix for suffix in ('p','n','x','s')]
    positive,negative=TV.from_json(hypothesis['positive']),TV.from_json(hypothesis['negative'])
    expressions=[f'(Truth_ModusPonens {sensor.metta()} {positive.metta()})',
        f'(Truth_ModusPonens {sensor.metta()} {negative.metta()})',f'(Truth_Negation ({names[1]}))',
        f'(let ($tv $ev) (BestConfidenceCandidate ((({names[0]}) (positive)) (({names[2]}) (negative)))) $tv)']
    observation_premise=dict(observation_id=observation['id'],predicate='ObservedRelativeContext',
        truth_value=sensor.json(),descriptor=observation['descriptor'],facts=observation['facts'],source=observation['source'])
    premises=[
        [observation_premise,dict(hypothesis=observation['rule_id'],channel='positive',truth_value=positive.json())],
        [observation_premise,dict(hypothesis=observation['rule_id'],channel='negative',truth_value=negative.json())],
        [dict(node=names[1])],[dict(node=names[0]),dict(node=names[2])]]
    operators=('Truth_ModusPonens','Truth_ModusPonens','Truth_Negation','BestConfidenceCandidate')
    traces=[]
    for i,(name,expression,operator,premise) in enumerate(zip(names,expressions,operators,premises)):
        traces.append(dict(id=name,operator=operator,native_expression=expression,
            conclusion=dict(predicate=observation['target'],relation_id=observation['relation_id'],negated=i==1),
            premises=premise,matched_rule_ids=[observation['rule_id']],
            evidence_ids=sorted(set(hypothesis['evidence_ids']+[observation['id']])),
            dependence_groups=hypothesis['dependence_groups'],observation_id=observation['id'],
            model_version=model_version,runtime_version=runtime_version,
            proof_scope='Native TV rule on a host-grounded typed conditional; no conjunction introduction or global composition.'))
    return list(zip(names,expressions)),traces,names[-1]


def infer_queries(queries,model,options=None,runtime=None,session=None):
    started=time.perf_counter()
    options=options or FieldOptions()
    if not isinstance(queries,(list,tuple)) or len(queries)>4096:
        raise ValueError('A field batch supports at most 4096 explicit source/target queries')
    runtime=runtime or Runtime(timeout=options.timeout_seconds)
    model.validate(runtime)
    model_version=model.version
    session=session or FieldSession(runtime)
    if session.runtime is not runtime:
        raise ValueError('The field session belongs to a different runtime instance')
    start_calls,start_hits,start_invalidations=runtime.invocations,session.native.hits,session.invalidations
    session.bind(digest([model_version,runtime.manifest,asdict(options)]))
    sensor=TV(1.,options.sensor_confidence)
    bindings,pending,jobs,snapshots=[],{},[],{}
    logical_nodes,relation_hits=0,0
    truncated=False
    error=None
    for query in queries:
        if not isinstance(query,dict) or not isinstance(query.get('id'),str):
            raise ValueError('Every field query requires a string identity')
        position=Position.from_fen(query['position']) if isinstance(query['position'],str) else query['position']
        if not isinstance(position,Position):
            raise ValueError('A field query requires a supplied position')
        if id(position) not in snapshots:
            validate_position(position)
            snapshots[id(position)]=snapshot_id(position)
        source_square=parse_square(query['source_square'])
        target=parse_square(query['target_square'])
        piece=position.at(source_square)
        families=query.get('families',FIELDS)
        if not isinstance(families,(list,tuple)) or not families or len(set(families))!=len(families) or any(f not in TARGETS for f in families):
            raise ValueError('Choose distinct registered field families')
        for family in families:
            observation=observe_relation(position,piece,target,family,source=query.get('source','supplied-field-context'))
            hypothesis=model.hypotheses.get(observation['rule_id'])
            record=_record(observation,hypothesis,model_version,runtime.version)
            viable=observation['complete'] and observation['applicable'] and hypothesis is not None and sensor.confidence>0
            if viable and not any(hypothesis[channel]['confidence']>0 for channel in ('positive','negative')):
                viable=False
                record['gaps'].append('The learned conditional has no positive-confidence evidence.')
            if hypothesis is None:
                record['gaps'].append('No learned conditional matches this relative context.')
            if sensor.confidence==0:
                record['gaps'].append('The supplied context sensor has zero confidence.')
            budget_exhausted=viable and logical_nodes+4>options.max_native_invocations
            deadline_exhausted=time.perf_counter()-started>=options.timeout_seconds
            if budget_exhausted or deadline_exhausted:
                truncated=True
                record.update(classification='incomplete',proof_status='incomplete')
                record['gaps'].append('Native proof-node budget exhausted.' if budget_exhausted else 'Field inference deadline exhausted.')
            else:
                if viable:
                    # The logical proof budget applies even when its calculation
                    # or relation record is cached.
                    logical_nodes+=4
                cached=session.get(observation['relation_id'],observation['id'])
                if cached is not None:
                    record=cached
                    relation_hits+=1
                elif observation['id'] in pending:
                    record=pending[observation['id']]['record']
                elif viable:
                    nodes,trace,selected=_schedule(observation,hypothesis,model_version,runtime.version,sensor)
                    jobs.extend(nodes)
                    pending[observation['id']]=dict(record=record,trace=trace,selected=selected)
                else:
                    session.put(observation['relation_id'],observation['id'],record)
            bindings.append((record,query['id'],snapshots[id(position)]))
    if jobs:
        previous_timeout=runtime.timeout
        try:
            remaining=options.timeout_seconds-(time.perf_counter()-started)
            if remaining<=0:
                raise NativeError('Field inference deadline exhausted before native execution')
            runtime.timeout=min(previous_timeout,remaining)
            values=session.native.batch(jobs)
            for observation_id,plan in pending.items():
                record=plan['record']
                trace=[{**node,'truth_value':values[node['id']].json()} for node in plan['trace']]
                tv=values[plan['selected']]
                record.update(raw_stv=tv.json(),truth_value_origin='native',classification=classify(tv,options),
                    conditional_proof_complete=True,proof_trace=trace,proof_id=digest(trace),proof_status='native-local-conditional')
                if record['classification']=='unknown':
                    record['gaps'].append('Native conditional evidence is below the registered strength/confidence thresholds.')
                session.put(record['relation_id'],observation_id,record)
        except NativeError as failure:
            truncated=True
            error=str(failure)
            for plan in pending.values():
                plan['record'].update(classification='incomplete',proof_status='incomplete',planned_native_nodes=plan['trace'])
                plan['record']['gaps'].append('Native execution failed; no host inference fallback: '+error)
        finally:
            runtime.timeout=previous_timeout
    # Query and complete-state bindings never reside in reusable local records.
    relations=[{**copy.deepcopy(record),'query_id':query_id,'snapshot_id':state_id} for record,query_id,state_id in bindings]
    proof_bytes=sum(len(canonical(record['proof_trace']).encode()) for record in relations)
    return dict(schema='relative-field-query-result-v11',model_version=model_version,runtime_version=runtime.version,
        relations=relations,mode='experimental-field-conditional',native_invocations=runtime.invocations-start_calls,
        scheduled_invocations=len(jobs),logical_native_nodes=logical_nodes,cache_hits=session.native.hits-start_hits,
        relation_cache_hits=relation_hits,relation_cache_invalidations=session.invalidations-start_invalidations,
        grounded_atoms=sum(len(r['observation']['facts'])+len(r['proof_trace']) for r in relations),
        proof_bytes=proof_bytes,elapsed_seconds=time.perf_counter()-started,truncated=truncated,error=error,
        cost_semantics='Scheduled nodes precede pure native math reuse; native invocations count executed operators. Grounded atoms count logical observation-fact and proof-node appearances in returned relations. Proof bytes measure serialized native traces.',
        strategic_score=None,global_composition_complete=False)


def build_field(position,model,*,options=None,runtime=None,session=None,source='supplied-field-context',families=None,source_ids=None):
    position=Position.from_fen(position) if isinstance(position,str) else position
    validate_position(position)
    families=tuple(families or FIELDS)
    if not families or len(set(families))!=len(families) or any(f not in TARGETS for f in families):
        raise ValueError('Unknown or repeated field family')
    selected=set(source_ids) if source_ids is not None else {piece.id for piece in position.pieces}
    unknown=set(position.unknown_squares)
    jobs=[]
    for piece in sorted(position.pieces,key=lambda p:p.id):
        if piece.id not in selected:
            continue
        for y in range(8):
            for x in range(8):
                target=(x,y)
                if target==piece.square:
                    continue
                occupant=position.at(target) if target not in unknown else None
                included=[]
                for family in families:
                    if family=='defense' and target not in unknown and (occupant is None or occupant.owner!=piece.owner):
                        continue
                    if family=='king-exposure' and target not in unknown and (occupant is None or occupant.owner==piece.owner or occupant.kind!='King'):
                        continue
                    included.append(family)
                if included:
                    jobs.append(dict(id='field-query:'+digest([piece.id,list(target),included])[:24],position=position,
                        source_square=square_name(piece.square),target_square=square_name(target),families=included,source=source))
    result=infer_queries(jobs,model,options,runtime,session)
    directional,projection={},{}
    for relation in result['relations']:
        directional.setdefault(relation['source_entity'],{}).setdefault(','.join(map(str,relation['relative_displacement'])),[]).append(relation['relation_id'])
        projection.setdefault(relation['target_square'],[]).append(dict(relation_id=relation['relation_id'],
            source_entity=relation['source_entity'],family=relation['family'],classification=relation['classification'],
            raw_stv=relation['raw_stv'],intensity=None))
    counts={family:{classification:sum(r['family']==family and r['classification']==classification for r in result['relations'])
        for classification in ('supported','contradicted','unknown','incomplete')} for family in families}
    return dict(schema='relative-field-snapshot-v11',fen=position.fen(),position_id=position.id,snapshot_id=snapshot_id(position),
        unknown_squares=[list(square) for square in sorted(unknown)],pieces=[asdict(p) for p in position.pieces],
        model_version=result['model_version'],runtime_version=result['runtime_version'],families=list(families),
        selected_source_entities=sorted(selected),missing_selected_entities=sorted(selected-{p.id for p in position.pieces}),
        relations=result['relations'],graph=dict(kind='typed-relational-influence',edges=[r['relation_id'] for r in result['relations']]),
        directional_index=directional,projection=projection,classification_counts=counts,
        execution={k:v for k,v in result.items() if k not in ('relations','model_version','runtime_version','schema')},
        uncertainty=dict(unknown_cells=len(unknown),observed_kings={owner:sum(p.kind=='King' and p.owner==owner and p.square not in unknown for p in position.pieces) for owner in ('White','Black')},
            universal_safety_proved=False,legal_recapture_proved=False),
        provenance=dict(source=source,scope='Conditional on the supplied structural environment; no claim that it is a verified legal game state.'),
        visualization_scope='Board coordinates and colors are projections of separate relations. No combined truth value, calibrated confidence, strategic score or move ranking is computed.')
