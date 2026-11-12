"""Content-addressed JSON DAG with exact expansion and durable request handles.

This is host proof storage, not a native inference engine. Shared storage never
removes an occurrence from an ordered premise/evidence list.
"""
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading
import zlib

from pln_chess.common import canonical, digest

SCHEMA='pln-proof-dag-v14'
DOMAIN=b'pln-proof-object-v14\0'


class ProofError(ValueError):
    pass


@dataclass(frozen=True,slots=True)
class Ref:
    id: str

    def __post_init__(self):
        if not isinstance(self.id,str) or not re.fullmatch(r'[0-9a-f]{64}',self.id):
            raise ProofError('Invalid content-addressed proof reference')


def object_id(encoded):
    return hashlib.sha256(DOMAIN+canonical(encoded).encode()).hexdigest()


def dependencies(encoded):
    if not isinstance(encoded,list) or len(encoded)!=2 or encoded[0] not in ('dict','list','scalar'):
        raise ProofError('Invalid proof-object encoding')
    kind,value=encoded
    if kind=='scalar':
        if isinstance(value,(dict,list)):raise ProofError('Container encoded as scalar')
        canonical(value)
        return []
    if not isinstance(value,list):raise ProofError('Invalid proof-object children')
    if kind=='dict':
        if any(not isinstance(row,list) or len(row)!=2 or not isinstance(row[0],str) for row in value):
            raise ProofError('Invalid dictionary entries')
        keys=[row[0] for row in value]
        if keys!=sorted(set(keys)):raise ProofError('Noncanonical dictionary keys')
        tokens=[row[1] for row in value]
    else:tokens=value
    refs=[]
    for token in tokens:
        if not isinstance(token,list) or len(token)!=2:raise ProofError('Invalid proof-object token')
        tag,payload=token
        if tag=='ref':refs.append(Ref(payload).id)
        elif tag=='value':
            if isinstance(payload,(dict,list)):raise ProofError('Inline container is not canonical')
            canonical(payload)
        else:raise ProofError('Unsupported proof-object token')
    return refs


class ProofStore:
    def __init__(self,path=':memory:',*,cache_entries=2048):
        if path!=':memory:':Path(path).parent.mkdir(parents=True,exist_ok=True)
        self.path=str(path);self.lock=threading.RLock();self.cache_entries=cache_entries
        self.cache=OrderedDict();self.hits=0;self.misses=0
        self.write_depth=0;self.written=set()
        self.db=sqlite3.connect(self.path,timeout=60,check_same_thread=False)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS objects (id TEXT PRIMARY KEY,payload BLOB NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY,identity TEXT UNIQUE NOT NULL,root TEXT NOT NULL,summary TEXT NOT NULL)')
        existing=self.db.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()
        if existing and existing[0]!=SCHEMA:
            self.db.close();raise ProofError('Proof-store schema mismatch')
        self.db.execute("INSERT OR IGNORE INTO metadata VALUES ('schema',?)",(SCHEMA,));self.db.commit()

    def close(self):
        with self.lock:self.db.close();self.cache.clear()

    def __enter__(self):return self
    def __exit__(self,*args):self.close()

    @contextmanager
    def transaction(self):
        """Batch durable writes without committing nested object insertions."""
        with self.lock:
            if self.write_depth:
                yield
                return
            self.write_depth=1;self.written=set()
            try:
                with self.db:yield
            finally:
                self.write_depth=0;self.written.clear()

    def put(self,value):
        """Intern a value or a template containing typed references, atomically."""
        memo={};active=set()
        def token(node):
            if isinstance(node,Ref):
                if not self.db.execute('SELECT 1 FROM objects WHERE id=?',(node.id,)).fetchone():
                    raise ProofError('Missing referenced proof object: '+node.id)
                return ['ref',node.id]
            if isinstance(node,(dict,list,tuple)):return ['ref',walk(node).id]
            canonical(node)
            return ['value',node]
        def walk(node):
            if isinstance(node,Ref):token(node);return node
            container=isinstance(node,(dict,list,tuple));marker=id(node)
            if container and marker in active:raise ProofError('Cyclic proof input')
            if container and marker in memo:return memo[marker]
            if container:active.add(marker)
            if isinstance(node,dict):
                if any(not isinstance(key,str) for key in node):raise ProofError('Proof keys must be strings')
                encoded=['dict',[[key,token(node[key])] for key in sorted(node)]]
            elif isinstance(node,(list,tuple)):encoded=['list',[token(item) for item in node]]
            else:canonical(node);encoded=['scalar',node]
            raw=canonical(encoded).encode();identifier=hashlib.sha256(DOMAIN+raw).hexdigest()
            if identifier not in self.written:
                self.db.execute('INSERT OR IGNORE INTO objects VALUES (?,?)',(identifier,zlib.compress(raw,1)))
                self.written.add(identifier)
            result=Ref(identifier)
            if container:active.remove(marker);memo[marker]=result
            return result
        with self.transaction():return walk(value)

    def _read(self,identifier):
        Ref(identifier)
        # Integrity verification is performed from durable bytes on every fetch.
        # The small decoded-object cache avoids reparsing, not verification.
        row=self.db.execute('SELECT payload FROM objects WHERE id=?',(identifier,)).fetchone()
        if row is None:raise ProofError('Missing referenced proof object: '+identifier)
        try:raw=zlib.decompress(row[0])
        except zlib.error as error:raise ProofError('Corrupt compressed proof object: '+identifier) from error
        if hashlib.sha256(DOMAIN+raw).hexdigest()!=identifier:raise ProofError('Corrupt proof object identity: '+identifier)
        if identifier in self.cache:
            self.cache.move_to_end(identifier);return self.cache[identifier]
        try:encoded=json.loads(raw)
        except (json.JSONDecodeError,UnicodeDecodeError) as error:raise ProofError('Corrupt proof JSON') from error
        dependencies(encoded)
        self.cache[identifier]=encoded
        while len(self.cache)>self.cache_entries:self.cache.popitem(last=False)
        return encoded

    def expand(self,root,*,max_nodes=2000000):
        """Construct the full legacy JSON only on explicit archive demand."""
        remaining=max_nodes;active=set();verified={}
        def read(identifier):
            if identifier not in verified:verified[identifier]=self._read(identifier)
            return verified[identifier]
        def walk(identifier):
            nonlocal remaining
            remaining-=1
            if remaining<0:raise ProofError('Full proof expansion exceeds its explicit node budget')
            if identifier in active:raise ProofError('Cyclic stored proof')
            active.add(identifier);kind,value=read(identifier)
            def item(token):return walk(token[1]) if token[0]=='ref' else token[1]
            if kind=='dict':result={key:item(token) for key,token in value}
            elif kind=='list':result=[item(token) for token in value]
            else:result=value
            active.remove(identifier);return result
        with self.lock:return walk(root.id if isinstance(root,Ref) else Ref(root).id)

    def canonical_chunks(self,root,*,omit_keys=(),max_nodes=2000000):
        """Stream canonical legacy JSON; no expanded response allocation."""
        remaining=max_nodes;active=set();omitted=set(omit_keys);verified={}
        def read(identifier):
            if identifier not in verified:verified[identifier]=self._read(identifier)
            return verified[identifier]
        def walk(identifier):
            nonlocal remaining
            remaining-=1
            if remaining<0:raise ProofError('Proof stream exceeds its explicit node budget')
            if identifier in active:raise ProofError('Cyclic stored proof')
            active.add(identifier);kind,value=read(identifier)
            def item(token):
                if token[0]=='ref':yield from walk(token[1])
                else:yield canonical(token[1]).encode()
            if kind=='dict':
                yield b'{';first=True
                for key,token in value:
                    if key in omitted:continue
                    if not first:yield b','
                    first=False;yield canonical(key).encode();yield b':'
                    yield from item(token)
                yield b'}'
            elif kind=='list':
                yield b'['
                for index,token in enumerate(value):
                    if index:yield b','
                    yield from item(token)
                yield b']'
            else:yield canonical(value).encode()
            active.remove(identifier)
        with self.lock:yield from walk(root.id if isinstance(root,Ref) else Ref(root).id)

    def legacy_digest(self,root,*,omit_keys=()):
        result=hashlib.sha256()
        for chunk in self.canonical_chunks(root,omit_keys=omit_keys):result.update(chunk)
        return result.hexdigest()

    def reachable(self,root,*,max_nodes=500000):
        identifier=root.id if isinstance(root,Ref) else Ref(root).id
        pending=[identifier];seen=set();ordered=[]
        with self.lock:
            while pending:
                current=pending.pop()
                if current in seen:continue
                if len(seen)>=max_nodes:raise ProofError('Proof graph exceeds its explicit node budget')
                seen.add(current);ordered.append(current)
                pending.extend(reversed(dependencies(self._read(current))))
        return ordered

    def page(self,root,*,offset=0,limit=64):
        if type(offset) is not int or offset<0 or type(limit) is not int or not 1<=limit<=256:
            raise ProofError('Invalid proof pagination')
        identifiers=self.reachable(root)
        with self.lock:
            nodes=[dict(id=i,encoded=json.loads(canonical(self._read(i))),dependencies=dependencies(self._read(i)))
                for i in identifiers[offset:offset+limit]]
        return dict(schema=SCHEMA,root=root.id if isinstance(root,Ref) else root,offset=offset,limit=limit,
            total=len(identifiers),nodes=nodes,next_offset=offset+limit if offset+limit<len(identifiers) else None,
            graph_kind='host-content-addressed-audit-DAG',native_resident=False)

    def archive(self,root):
        identifiers=self.reachable(root)
        with self.lock:
            result=dict(schema=SCHEMA,root=root.id if isinstance(root,Ref) else root,
                objects={i:json.loads(canonical(self._read(i))) for i in sorted(identifiers)},
                canonical_legacy_sha256=self.legacy_digest(root),
                comparison_exclusions=[],evidence_occurrence_order_preserved=True)
        result['manifest_sha256']=digest(result)
        return result

    def import_archive(self,archive):
        expected=archive.get('manifest_sha256')
        if expected!=digest({k:v for k,v in archive.items() if k!='manifest_sha256'}):
            raise ProofError('Archive manifest integrity mismatch')
        if archive.get('schema')!=SCHEMA or not isinstance(archive.get('objects'),dict):
            raise ProofError('Unsupported proof archive')
        objects=archive['objects'];root=Ref(archive['root'])
        if root.id not in objects:raise ProofError('Missing archive root')
        for identifier,encoded in objects.items():
            if object_id(encoded)!=identifier:raise ProofError('Archive object integrity mismatch')
            if any(child not in objects for child in dependencies(encoded)):
                raise ProofError('Incomplete proof archive')
        with self.lock,self.db:
            for identifier,encoded in objects.items():
                self.db.execute('INSERT OR IGNORE INTO objects VALUES (?,?)',
                    (identifier,zlib.compress(canonical(encoded).encode(),1)))
            if self.legacy_digest(root)!=archive['canonical_legacy_sha256']:
                raise ProofError('Reconstructed legacy identity mismatch')
            if set(self.reachable(root))!=set(objects):raise ProofError('Unreachable objects in archive')
        return root

    def publish(self,root,summary,identity):
        root=root if isinstance(root,Ref) else Ref(root);identity_hash=digest(identity)
        identifier='proof-request:'+digest([SCHEMA,identity,root.id,summary])
        payload=canonical(dict(summary=summary,identity=identity))
        with self.lock,self.db:
            self._read(root.id)
            old=self.db.execute('SELECT id,root,summary FROM requests WHERE identity=?',(identity_hash,)).fetchone()
            if old:
                if old!=(identifier,root.id,payload):raise ProofError('Conflicting immutable request identity')
            else:self.db.execute('INSERT INTO requests VALUES (?,?,?,?)',(identifier,identity_hash,root.id,payload))
        return identifier

    def request(self,identifier):
        with self.lock:
            row=self.db.execute('SELECT root,summary FROM requests WHERE id=?',(identifier,)).fetchone()
            if row is None:raise ProofError('Unknown proof request')
            root,payload=row;self._read(root);decoded=json.loads(payload)
            if identifier!='proof-request:'+digest([SCHEMA,decoded['identity'],root,decoded['summary']]):
                raise ProofError('Corrupt proof request identity')
            return dict(handle=identifier,root=root,**decoded)

    def lookup(self,identity):
        with self.lock:
            row=self.db.execute('SELECT id FROM requests WHERE identity=?',(digest(identity),)).fetchone()
            if row is None:self.misses+=1;return None
            self.hits+=1;return self.request(row[0])

    def census(self):
        with self.lock:
            return dict(host_stored_objects=self.db.execute('SELECT COUNT(*) FROM objects').fetchone()[0],
                cached_requests=self.db.execute('SELECT COUNT(*) FROM requests').fetchone()[0],
                decoded_cache_entries=len(self.cache),request_cache_hits=self.hits,request_cache_misses=self.misses,
                native_resident_atoms=0,storage_scope='Host proof index, not persistent native reasoning state')
