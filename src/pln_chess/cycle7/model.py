"""Versioned optional conditionals. The frozen C6 source is preserved intact."""
import copy
from dataclasses import dataclass, asdict, field
from pathlib import Path
from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import TV
from pln_chess.cycle6.model import ModeModel

LEVELS=('exact','ray-contents-masked','destination-and-ray-masked')

def projection(descriptor, level):
    if level not in range(3):raise ValueError('Unknown backoff level')
    remove=() if level==0 else ('ray_contents',) if level==1 else ('ray_contents','destination')
    return {k:v for k,v in descriptor.items() if k not in remove}

def key(descriptor, level):
    return 'c7:'+digest([level,projection(descriptor,level)])[:24]

@dataclass
class BackoffModel:
    source:dict
    hypotheses:dict=field(default_factory=dict)
    training_report:dict=field(default_factory=dict)
    variant:str='C7-frozen'
    schema:int=7
    grammar:str='bounded-conditional-backoff-v7'
    @property
    def version(self):return digest(asdict(self))
    @property
    def runtime_version(self):return self.source['source']['runtime_version']
    def source_model(self):return ModeModel(**copy.deepcopy(self.source))
    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return {'path':str(path),'version':self.version,'schema':7}
    def inspect_hypothesis(self,k):
        return {'id':k,**self.hypotheses.get(k,{}),'model_version':self.version}
    @classmethod
    def migrate(cls,model):
        if model.schema!=6:raise ValueError('Cycle 7 requires a verified schema-6 checkpoint')
        return cls(asdict(model))
    @classmethod
    def load(cls,path,runtime=None):
        d=read_json(path);expected=d.pop('version');m=cls(**d)
        if m.schema!=7 or m.grammar!='bounded-conditional-backoff-v7' or m.version!=expected:raise ValueError('Cycle 7 checkpoint integrity/schema mismatch')
        if runtime and m.runtime_version!=runtime.version:raise ValueError('Cycle 7 runtime mismatch')
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.json';m.source_model().export(p);ModeModel.load(p,runtime)
        for k,h in m.hypotheses.items():
            if k!=key(h['descriptor'],h['level']) or h['level'] not in range(3):raise ValueError('Invalid backoff descriptor')
            TV.from_json(h['positive']);TV.from_json(h['negative'])
            if not h['evidence_ids'] or not h['dependence_groups']:raise ValueError('Missing backoff provenance')
        return m
