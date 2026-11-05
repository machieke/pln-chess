"""Lossless schema-5 migration: no retraining or new native mathematics."""
from dataclasses import dataclass,asdict
from pathlib import Path
import copy
from pln_chess.common import digest,read_json,write_json
from pln_chess.cycle5.model import PremiseModel

POLICY='evidence-channels-v6.1'
@dataclass
class ModeModel:
    source:dict
    schema:int=6
    grammar:str='explicit-proof-modes-v6'
    variant:str='C6-full'
    policy:str=POLICY

    @property
    def runtime_version(self):return self.source['runtime_version']
    @property
    def hypotheses(self):return self.source['hypotheses']
    @property
    def training_report(self):return self.source['training_report']
    @property
    def version(self):return digest(asdict(self))
    def source_model(self):return PremiseModel(**copy.deepcopy(self.source))
    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return {'path':str(path),'version':self.version,'schema':6}
    def inspect_hypothesis(self,key):
        source=self.source_model()
        return {**source.inspect_hypothesis(key),'model_version':self.version,'source_model_version':source.version}
    @classmethod
    def migrate(cls,model):
        if getattr(model,'schema',None)!=5:raise ValueError('Cycle 6 migration requires an intact Cycle 5 checkpoint')
        return cls(asdict(model))
    @classmethod
    def load(cls,path,runtime=None):
        d=read_json(path);version=d.pop('version');model=cls(**d)
        if model.schema!=6 or model.grammar!='explicit-proof-modes-v6' or model.policy!=POLICY:raise ValueError('Unsupported Cycle 6 schema/policy')
        if model.variant not in ('C6-full','C6-no-new-negatives'):raise ValueError('Unknown Cycle 6 variant')
        if model.version!=version:raise ValueError('Checkpoint integrity mismatch')
        # Reuse all schema-5 integrity and semantic checks on the embedded source.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.json';source=model.source_model();source.export(p);PremiseModel.load(p,runtime)
        return model
