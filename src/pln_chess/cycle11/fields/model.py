"""Self-contained experimental relative conditionals with native evidence TVs."""
from dataclasses import dataclass, field, asdict

from pln_chess.common import digest_dataclass, read_json, write_json
from pln_chess.pln import TV
from .ontology import GRAMMAR, TARGETS, key


@dataclass
class FieldModel:
    runtime_version: str
    hypotheses: dict = field(default_factory=dict)
    training_report: dict = field(default_factory=dict)
    ledger_digest: str = ''
    variant: str = 'C11-field-experimental'
    schema: str = 'relative-field-model-v11'
    grammar: str = GRAMMAR

    @property
    def version(self):
        # Mutation must change identity; sessions cannot retain stale hypotheses.
        return digest_dataclass(self)

    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return dict(path=str(path),version=self.version,schema=self.schema)

    def validate(self,runtime=None):
        if self.schema!='relative-field-model-v11' or self.grammar!=GRAMMAR:
            raise ValueError('Unsupported field-model schema or relative grammar')
        if not isinstance(self.runtime_version,str) or not self.runtime_version or (runtime is not None and self.runtime_version!=runtime.version):
            raise ValueError('Field checkpoint runtime identity mismatch')
        if not isinstance(self.hypotheses,dict) or not isinstance(self.training_report,dict):
            raise ValueError('Invalid field checkpoint structure')
        for identifier,hypothesis in self.hypotheses.items():
            family=hypothesis.get('family')
            if family not in TARGETS or hypothesis.get('target')!=TARGETS[family] or identifier!=key(family,hypothesis.get('descriptor')) or hypothesis.get('id')!=identifier:
                raise ValueError('Invalid typed relative field hypothesis')
            TV.from_json(hypothesis['positive'])
            TV.from_json(hypothesis['negative'])
            if not hypothesis.get('evidence_ids') or not hypothesis.get('dependence_groups'):
                raise ValueError('Missing learned field evidence provenance')
            if not set(hypothesis.get('supporting_evidence',[])+hypothesis.get('contradicting_evidence',[])) <= set(hypothesis['evidence_ids']):
                raise ValueError('Invalid field evidence partition')
        return True

    @classmethod
    def load(cls,path,runtime=None):
        supplied=read_json(path)
        expected=supplied.pop('version',None)
        try:
            model=cls(**supplied)
            model.validate(runtime)
        except (TypeError,KeyError) as error:
            raise ValueError('Malformed field checkpoint') from error
        if model.version!=expected:
            raise ValueError('Field checkpoint integrity mismatch')
        return model
