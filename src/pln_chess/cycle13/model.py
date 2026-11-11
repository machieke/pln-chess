"""Separate experimental native preference conditionals, never legal defaults."""
from dataclasses import dataclass, field, asdict
from pln_chess.common import digest_dataclass, read_json, write_json
from pln_chess.pln import TV
from .ontology import GRAMMAR, ABSTRACTIONS, CHANNELS, key


@dataclass
class PreferenceModel:
    runtime_version: str
    abstraction: str = 'relational'
    variant: str = 'C13-preference-experimental'
    hypotheses: dict = field(default_factory=dict)
    training_report: dict = field(default_factory=dict)
    ledger_digest: str = ''
    schema: str = 'relative-preference-model-v13'
    grammar: str = GRAMMAR

    @property
    def version(self):
        return digest_dataclass(self)

    def validate(self, runtime=None):
        if self.schema != 'relative-preference-model-v13' or self.grammar != GRAMMAR or self.abstraction not in ABSTRACTIONS:
            raise ValueError('Unsupported preference checkpoint schema')
        if not isinstance(self.runtime_version,str) or not self.runtime_version or (runtime and runtime.version != self.runtime_version):
            raise ValueError('Preference checkpoint runtime mismatch')
        if not isinstance(self.hypotheses,dict) or not isinstance(self.training_report,dict):
            raise ValueError('Malformed preference checkpoint')
        for identifier, h in self.hypotheses.items():
            if key(h['descriptor']) != identifier or h['id'] != identifier or h['descriptor']['abstraction'] != self.abstraction:
                raise ValueError('Invalid relative conditional identity')
            if set(h['channels']) != set(CHANNELS) or set(h['supporting_evidence']) != set(CHANNELS):
                raise ValueError('Preference channels must remain separate')
            for value in h['channels'].values():
                TV.from_json(value)
            evidence = h['evidence_ids']
            support = [e for values in h['supporting_evidence'].values() for e in values]
            if not evidence or not h['dependence_groups'] or len(set(evidence)) != len(evidence) or sorted(support) != sorted(evidence):
                raise ValueError('Invalid preference evidence partition')
        return True

    def export(self, path):
        self.validate()
        write_json(path,{**asdict(self),'version':self.version})
        return dict(path=str(path),version=self.version,schema=self.schema)

    @classmethod
    def load(cls,path,runtime=None):
        data=read_json(path);expected=data.pop('version',None)
        try:
            model=cls(**data);model.validate(runtime)
        except (TypeError,KeyError) as error:
            raise ValueError('Malformed preference checkpoint') from error
        if expected != model.version:
            raise ValueError('Preference checkpoint integrity mismatch')
        return model
