"""Immutable C7 source plus separately replayable promotion evidence."""
from dataclasses import dataclass, asdict, field
import copy
from pathlib import Path
import tempfile
from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import TV
from pln_chess.cycle7.model import BackoffModel
from .ontology import GRAMMAR, key


@dataclass
class PromotionModel:
    source: dict
    hypotheses: dict = field(default_factory=dict)
    training_report: dict = field(default_factory=dict)
    variant: str = 'C8-promotion-relative'
    projection_variant: str = 'C8-promotion-relative'
    schema: int = 8
    grammar: str = GRAMMAR

    @property
    def version(self): return digest(asdict(self))
    @property
    def runtime_version(self): return self.source['source']['source']['runtime_version']
    def source_model(self): return BackoffModel(**copy.deepcopy(self.source))
    def export(self, path):
        write_json(path, {**asdict(self),'version':self.version})
        return {'path':str(path),'version':self.version,'schema':8}
    def inspect_hypothesis(self, identifier):
        return {'id':identifier,**self.hypotheses.get(identifier,{}),'model_version':self.version}

    @classmethod
    def wrap(cls, source, variant='C8-promotion-relative'):
        if source.schema != 7: raise ValueError('Cycle 8 requires a preserved C7 source')
        return cls(asdict(source),variant=variant)

    @classmethod
    def load(cls, path, runtime=None):
        data=read_json(path);expected=data.pop('version');model=cls(**data)
        if model.schema!=8 or model.grammar!=GRAMMAR or model.version!=expected:
            raise ValueError('Cycle 8 checkpoint integrity/schema mismatch')
        if model.projection_variant not in ('C8-promotion-relative','no-destination-context','no-choice-context'):
            raise ValueError('Unknown promotion projection')
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'source.json';model.source_model().export(source);BackoffModel.load(source,runtime)
        for identifier,h in model.hypotheses.items():
            if identifier!=key(h['descriptor'],model.projection_variant) or h['target']!='LocalAdmissibility':
                raise ValueError('Invalid promotion hypothesis')
            TV.from_json(h['positive']);TV.from_json(h['negative'])
            if not h['evidence_ids'] or not h['dependence_groups']:raise ValueError('Missing promotion provenance')
            if not set(h['supporting_evidence']+h['contradicting_evidence'])<=set(h['evidence_ids']):
                raise ValueError('Invalid promotion evidence partition')
        return model
