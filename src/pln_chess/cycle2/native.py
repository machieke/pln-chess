"""Memoize pure native calculations, preserving every logical proof node."""
import re
from pln_chess.common import digest


class NativeSession:
    def __init__(self,runtime,optimized=True):
        self.runtime=runtime; self.optimized=optimized; self.cache={}; self.calls=0; self.hits=0

    @property
    def version(self): return self.runtime.version

    def batch(self,nodes):
        refs={}; symbolic={}; jobs=[]; cached={}; identities={}
        for name,expr in nodes:
            # A digest of the exact pure expression and prerequisite identities.
            # No reordering, TV arithmetic, statistical fusion or evidence deduplication.
            keyexpr=re.sub(r'\(([A-Za-z][\w-]*)\)',lambda m:'(Dependency '+identities[m[1]]+')' if m[1] in identities else m[0],expr)
            key=digest([self.version,keyexpr]);identities[name]=key
            if self.optimized and key in self.cache:
                cached[name]=self.cache[key];refs[name]=self.cache[key].metta();self.hits+=1
            elif self.optimized and key in symbolic:
                refs[name]=refs[symbolic[key]];self.hits+=1
            else:
                native_expr=re.sub(r'\(([A-Za-z][\w-]*)\)',lambda m:refs.get(m[1],m[0]),expr)
                jobs.append((name,native_expr));refs[name]=f'({name})';symbolic[key]=name
        values=self.runtime.batch(jobs);self.calls+=len(jobs)
        result={}
        for name,expr in nodes:
            if name in cached: result[name]=cached[name]
            else:
                ref=refs[name];result[name]=values[ref[1:-1]]
            if self.optimized: self.cache[identities[name]]=result[name]
        return result
