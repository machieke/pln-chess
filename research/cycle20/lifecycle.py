"""Bounded host publication of immutable native generations."""
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from .native import derive,resume,fresh_input
from .observations import COMBINED
from .state import query_list,validate


@dataclass(frozen=True)
class Ticket:
    name: str
    epoch: int
    snapshot: str


class Generations:
    def __init__(self):
        self._lock=RLock()
        self._current={};self._epochs={};self._history={};self._cache={}
        self._models={};self._sources={}

    def begin(self,names):
        names=tuple(sorted(set(names)))
        if not names:raise ValueError('Empty replacement')
        with self._lock:
            for name in names:
                self._epochs[name]=self._epochs.get(name,0)+1
                self._current.pop(name,None)
            return {name:self._epochs[name] for name in names}

    def invalidate_model(self,model):
        with self._lock:
            return self.begin(k for k,v in self._models.items() if v==model)

    def invalidate_observation(self,capture):
        with self._lock:
            return self.begin(k for k,v in self._sources.items() if capture in v)

    def publish(self,pending,replacements):
        if not pending or pending.keys()!=replacements.keys():raise ValueError('Partial replacement')
        entries={}
        for name,(workspace,result) in replacements.items():
            identity=workspace.identity
            state=result['state'];sid=state['snapshot']
            validate(state,identity,sid)
            if result['derivations']!=1 or state['parent'] is not None:raise ValueError('Replacement requires raw-input derivation')
            inputs,_=fresh_input(workspace.facts,workspace.rules)
            if inputs!=state['inputs']:raise ValueError('Replacement input mismatch')
            entries[name]=(sid,identity,deepcopy(state),tuple(workspace.lineage['source_events']))
        with self._lock:
            if any(self._epochs.get(k)!=v or k in self._current for k,v in pending.items()):
                raise ValueError('Stale replacement transaction')
            for name,(sid,identity,state,sources) in entries.items():
                self._history[sid]=(identity,state)
                self._models[name]=identity.model;self._sources[name]=sources
                self._current[name]=sid
            return {name:self.ticket(name) for name in entries}

    def ticket(self,name):
        with self._lock:
            if name not in self._current:raise ValueError('Workspace unavailable for current use')
            return Ticket(name,self._epochs[name],self._current[name])

    def check(self,ticket):
        if self.ticket(ticket.name)!=ticket:raise ValueError('Stale generation')

    def rebuild(self,name,workspace):
        pending=self.begin([name])
        result=derive(workspace.facts,workspace.rules,workspace.queries,workspace.identity,COMBINED)
        return self.publish(pending,{name:(workspace,result)})[name],result

    def historic(self,snapshot,queries):
        with self._lock:identity,state=self._history[snapshot]
        return resume(state,identity,snapshot,queries)

    def read(self,ticket,queries):
        qs=query_list(queries);key=(ticket,tuple(qs))
        with self._lock:
            self.check(ticket)
            if key in self._cache:return deepcopy(self._cache[key]),True
        restored=self.historic(ticket.snapshot,qs)
        records=deepcopy(restored['readouts'])
        # A read-only restoration produces its own execution receipt. The served
        # generation is the validated source snapshot, also bound to the ticket.
        for row in records:
            row['restored_snapshot']=row['snapshot'];row['snapshot']=ticket.snapshot
        with self._lock:
            self.check(ticket)
            self._cache[key]=deepcopy(records)
            return records,False
