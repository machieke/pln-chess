"""Immutable records, explicit dependencies and atomic current-view replacement.

This is host policy, not native belief propagation. Statistical grouping is
metadata and never used as an invalidation edge.
"""
import copy
from collections import deque
from pln_chess.common import digest

POLICY='cycle19-active-evidence-v1'


class StaleEvidence(ValueError):pass


class Journal:
    def __init__(self):
        self._nodes={};self._active=set();self._stale=set();self._children={}
        self.pending=False;self.revision=0

    def node(self,ident):return copy.deepcopy(self._nodes[ident])

    def require(self,ident):
        if self.pending or ident not in self._active or ident in self._stale:
            raise StaleEvidence('Record is unavailable in the current view: '+ident)
        return self.node(ident)

    def add(self,kind,payload,parents=(),*,ident=None):
        parents=tuple(sorted(set(parents)))
        value=dict(kind=kind,payload=copy.deepcopy(payload),parents=list(parents))
        ident=ident or kind+'_'+digest(value)
        if ident in self._nodes:
            if self._nodes[ident]!=value:raise ValueError('Changed payload under immutable event ID')
            self.require(ident)
            return ident
        for parent in parents:self.require(parent)
        if self.pending:raise StaleEvidence('Rebuild pending')
        self._nodes[ident]=value;self._active.add(ident)
        for parent in parents:self._children.setdefault(parent,set()).add(ident)
        return ident

    def descendants(self,ident):
        found={ident};queue=deque([ident])
        while queue:
            for child in self._children.get(queue.popleft(),()):
                if child not in found:found.add(child);queue.append(child)
        return found

    def full_descendants(self,ident):
        found={ident}
        while True:
            expanded=found|{k for k,v in self._nodes.items() if set(v['parents'])&found}
            if expanded==found:return found
            found=expanded

    def snapshot(self):
        if self.pending:raise StaleEvidence('No mixed snapshot during rebuild')
        value=dict(policy=POLICY,nodes=copy.deepcopy(self._nodes),active=sorted(self._active),
            stale=sorted(self._stale),revision=self.revision)
        value['identity']=digest(value);return value

    @classmethod
    def historical(cls,snapshot):
        if snapshot['policy']!=POLICY:raise ValueError('Unknown snapshot policy')
        if snapshot['identity']!=digest({k:v for k,v in snapshot.items() if k!='identity'}):
            raise ValueError('Snapshot integrity mismatch')
        journal=cls();journal._nodes=copy.deepcopy(snapshot['nodes'])
        journal._active=set(snapshot['active']);journal._stale=set(snapshot['stale'])
        journal.revision=snapshot['revision']
        for child,value in journal._nodes.items():
            for parent in value['parents']:journal._children.setdefault(parent,set()).add(child)
        return journal

    def supersede(self,old,kind,payload,*,full=False):
        self.require(old)
        affected=self.full_descendants(old) if full else self.descendants(old)
        draft=copy.deepcopy(self);draft._stale.update(affected);draft._active.difference_update(affected)
        new=draft.add(kind,payload)
        if new==old:raise ValueError('Supersession requires changed evidence version')
        # Fail closed immediately. The published old snapshot stays replayable;
        # no current request may use it while the rebuild is pending.
        self._stale.update(affected);self.pending=True
        return Transaction(self,draft,old,new,affected)


class Transaction:
    def __init__(self,owner,draft,old,new,affected):
        self.owner=owner;self.draft=draft;self.old=old;self.new=new;self.affected=affected;self.closed=False

    def commit(self,required):
        if self.closed:raise ValueError('Transaction already closed')
        if not required:raise ValueError('Rebuild must identify its complete required outputs')
        for ident in required:self.draft.require(ident)
        old_models=[self.owner._nodes[k]['payload']['arm'] for k in self.affected if k in self.owner._active and self.owner._nodes[k]['kind']=='generation']
        new_models=[self.draft._nodes[k]['payload']['arm'] for k in required if self.draft._nodes[k]['kind']=='generation']
        if not set(old_models)<=set(new_models):raise ValueError('Affected parameter generations require explicit replacement')
        # Publication is one replacement of the in-memory view. Snapshots are
        # subsequently published as immutable atomic files by the CLI.
        self.draft.revision=self.owner.revision+1
        self.owner.__dict__=copy.deepcopy(self.draft.__dict__)
        self.closed=True
        return self.owner.snapshot()


class Cache:
    def __init__(self):self.rows={}

    def get(self,key,journal):
        item=self.rows.get(key)
        if item is None:return None
        journal.require(item['event'])
        return copy.deepcopy(item['result'])

    def put(self,key,result,journal,parents):
        event=journal.add('cache',dict(key=key,observable_hashes={k:v['observable_sha256'] for k,v in result['stages'].items()}),parents)
        self.rows[key]=dict(event=event,result=copy.deepcopy(result));return event
