"""Occupancy dependency scheduling with unchanged native field records."""
import copy
from dataclasses import asdict
import time

from pln_chess.common import canonical, digest
from pln_chess.domain import Position, square_name
from pln_chess.cycle11.fields.ontology import FIELDS, TARGETS, snapshot_id, validate_position
from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, build_field, infer_queries
from .ontology import structural_successor


def _query_layout(position,families,selected,source):
    unknown=set(position.unknown_squares)
    for piece in sorted(position.pieces,key=lambda p:p.id):
        if piece.id not in selected:continue
        for y in range(8):
            for x in range(8):
                target=(x,y)
                if target==piece.square:continue
                occupant=position.at(target) if target not in unknown else None
                included=[]
                for family in families:
                    if family=='defense' and target not in unknown and (occupant is None or occupant.owner!=piece.owner):continue
                    if family=='king-exposure' and target not in unknown and (occupant is None or occupant.owner==piece.owner or occupant.kind!='King'):continue
                    included.append(family)
                if included:
                    yield piece,dict(id='field-query:'+digest([piece.id,list(target),included])[:24],position=position,
                        source_square=square_name(piece.square),target_square=square_name(target),families=included,source=source)


def _assemble(position,model,runtime,families,selected,source,relations,execution):
    directional={};projection={}
    for relation in relations:
        directional.setdefault(relation['source_entity'],{}).setdefault(','.join(map(str,relation['relative_displacement'])),[]).append(relation['relation_id'])
        projection.setdefault(relation['target_square'],[]).append(dict(relation_id=relation['relation_id'],
            source_entity=relation['source_entity'],family=relation['family'],classification=relation['classification'],
            raw_stv=relation['raw_stv'],intensity=None))
    counts={family:{classification:sum(r['family']==family and r['classification']==classification for r in relations)
        for classification in ('supported','contradicted','unknown','incomplete')} for family in families}
    unknown=set(position.unknown_squares)
    return dict(schema='relative-field-snapshot-v11',fen=position.fen(),position_id=position.id,snapshot_id=snapshot_id(position),
        unknown_squares=[list(square) for square in sorted(unknown)],pieces=[asdict(p) for p in position.pieces],
        model_version=model.version,runtime_version=runtime.version,families=list(families),selected_source_entities=sorted(selected),
        missing_selected_entities=sorted(selected-{p.id for p in position.pieces}),relations=relations,
        graph=dict(kind='typed-relational-influence',edges=[r['relation_id'] for r in relations]),directional_index=directional,
        projection=projection,classification_counts=counts,execution=execution,
        uncertainty=dict(unknown_cells=len(unknown),observed_kings={owner:sum(p.kind=='King' and p.owner==owner and p.square not in unknown for p in position.pieces)
            for owner in ('White','Black')},universal_safety_proved=False,legal_recapture_proved=False),
        provenance=dict(source=source,scope='Conditional on the supplied structural environment; no claim that it is a verified legal game state.'),
        visualization_scope='Board coordinates and colors are projections of separate relations. No combined truth value, calibrated confidence, strategic score or move ranking is computed.')


class IncrementalFieldSession:
    def __init__(self,runtime):
        self.runtime=runtime;self.fields=FieldSession(runtime)
        self.scope=None;self.position=None;self.lookup={};self.proof_sizes={};self.complete=False

    def _remember_full(self,position,scope,result):
        self.position=position;self.scope=scope;self.complete=not result['execution']['truncated']
        self.lookup={(r['source_entity'],r['target_square'],r['family']):copy.deepcopy(r) for r in result['relations']}
        self.proof_sizes={r['proof_id']:len(canonical(r['proof_trace']).encode()) for r in result['relations']}

    def build(self,position,model,*,options=None,source='supplied-field-context',families=None,source_ids=None):
        started=time.perf_counter();options=options or FieldOptions()
        position=Position.from_fen(position) if isinstance(position,str) else position
        validate_position(position);model.validate(self.runtime)
        families=tuple(families or FIELDS)
        if not families or len(set(families))!=len(families) or any(f not in TARGETS for f in families):
            raise ValueError('Unknown or repeated field family')
        selected=set(source_ids) if source_ids is not None else {p.id for p in position.pieces}
        scope=digest([model.version,self.runtime.manifest,asdict(options),source,families,
            sorted(selected) if source_ids is not None else None])
        layout=list(_query_layout(position,families,selected,source))
        total=sum(len(query['families']) for _,query in layout)
        if scope!=self.scope or self.position is None or not self.complete or options.max_native_invocations<4*total:
            result=build_field(position,model,options=options,runtime=self.runtime,session=self.fields,
                source=source,families=families,source_ids=source_ids)
            reason='initial-or-rebound-scope' if scope!=self.scope or self.position is None else 'full-reference-for-budget-or-incomplete-parent'
            self._remember_full(position,scope,result)
            result['incremental']=dict(path='full',reason=reason,reused_relations=0,scheduled_relations=len(result['relations']),
                changed_cells=[],metadata_invalidations=0,host_scheduling_only=True)
            return result
        before={p.square:(p.id,p.kind,p.owner) for p in self.position.pieces}
        after={p.square:(p.id,p.kind,p.owner) for p in position.pieces}
        changed={square for square in before.keys()|after.keys() if before.get(square)!=after.get(square)}
        changed|=set(self.position.unknown_squares)^set(position.unknown_squares)
        ep_changed=self.position.ep!=position.ep
        state_id=snapshot_id(position);slots=[];jobs=[];reused=0;metadata_invalidations=0;next_lookup={}
        for piece,query in layout:
            affected=[]
            for family in query['families']:
                identifier=(piece.id,query['target_square'],family);old=self.lookup.get(identifier)
                metadata=ep_changed and family=='mobility'
                deps={tuple(d['square']) for d in old['observation']['dependencies']} if old else set()
                invalid=old is None or bool(deps&changed) or metadata
                if metadata and old is not None:metadata_invalidations+=1
                if invalid:
                    affected.append(family);slots.append((identifier,None))
                else:
                    # Private local proof records can be shared internally;
                    # caller and full-state bindings are always fresh copies.
                    record=copy.deepcopy(old);record['query_id']=query['id'];record['snapshot_id']=state_id
                    slots.append((identifier,record));next_lookup[identifier]=old;reused+=1
            if affected:jobs.append({**query,'families':affected})
        calls=self.runtime.invocations;previous_timeout=self.runtime.timeout
        try:
            self.runtime.timeout=min(previous_timeout,max(.001,options.timeout_seconds-(time.perf_counter()-started)))
            updates=infer_queries(jobs,model,options,self.runtime,self.fields)
        finally:self.runtime.timeout=previous_timeout
        changed_records={(r['source_entity'],r['target_square'],r['family']):r for r in updates['relations']}
        relations=[];sizes={}
        for identifier,record in slots:
            if record is None:
                record=changed_records[identifier];next_lookup[identifier]=copy.deepcopy(record)
            relations.append(record)
            proof=record['proof_id']
            if proof not in sizes:
                sizes[proof]=self.proof_sizes[proof] if proof in self.proof_sizes else len(canonical(record['proof_trace']).encode())
        execution={k:v for k,v in updates.items() if k not in ('relations','model_version','runtime_version','schema')}
        execution.update(native_invocations=self.runtime.invocations-calls,
            logical_native_nodes=updates['logical_native_nodes']+sum(4 for _,record in slots if record and record['conditional_proof_complete']),
            relation_cache_hits=updates['relation_cache_hits']+reused,
            grounded_atoms=sum(len(r['observation']['facts'])+len(r['proof_trace']) for r in relations),
            proof_bytes=sum(sizes[r['proof_id']] for r in relations),elapsed_seconds=time.perf_counter()-started)
        if execution['elapsed_seconds']>=options.timeout_seconds:
            # No invalid inference result is substituted. Preserve the valid
            # endpoint proofs and disclose that the overall request was late.
            execution['truncated']=True;execution['error']='Incremental field request exceeded its wall deadline'
        result=_assemble(position,model,self.runtime,families,selected,source,relations,execution)
        result['incremental']=dict(path='dependency-scheduled',reused_relations=reused,
            scheduled_relations=len(updates['relations']),changed_cells=[square_name(s) for s in sorted(changed)],
            metadata_invalidations=metadata_invalidations,host_scheduling_only=True,
            scope='Dependency indexes choose work. Native conditional inference and truth values are unchanged.')
        self.position=position;self.scope=scope;self.lookup=next_lookup;self.proof_sizes=sizes;self.complete=not execution['truncated']
        return result
