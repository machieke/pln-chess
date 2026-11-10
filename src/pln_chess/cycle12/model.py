"""Runtime-bound learned local concept conditionals; never a legal checkpoint."""
from dataclasses import dataclass, field, asdict
from pln_chess.common import digest_dataclass, read_json, write_json
from pln_chess.pln import TV
from .ontology import GRAMMAR, CONCEPTS, key


@dataclass
class ConceptModel:
    runtime_version:str
    hypotheses:dict=field(default_factory=dict)
    training_report:dict=field(default_factory=dict)
    ledger_digest:str=''
    variant:str='C12-concept-experimental'
    schema:str='relative-concept-model-v12'
    grammar:str=GRAMMAR

    @property
    def version(self):return digest_dataclass(self)

    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return dict(path=str(path),version=self.version,schema=self.schema)

    def validate(self,runtime=None):
        if self.schema!='relative-concept-model-v12' or self.grammar!=GRAMMAR:raise ValueError('Unsupported concept schema/grammar')
        if not isinstance(self.runtime_version,str) or not self.runtime_version or (runtime and self.runtime_version!=runtime.version):
            raise ValueError('Concept checkpoint runtime mismatch')
        if not isinstance(self.hypotheses,dict) or not isinstance(self.training_report,dict):raise ValueError('Invalid concept checkpoint')
        for identifier,h in self.hypotheses.items():
            if not isinstance(h,dict):raise ValueError('Invalid concept conditional record')
            concept=h.get('concept')
            if concept not in CONCEPTS or h.get('target')!=CONCEPTS[concept]['target'] or h.get('id')!=identifier or key(concept,h.get('descriptor'))!=identifier:
                raise ValueError('Invalid typed concept conditional')
            TV.from_json(h['positive']);TV.from_json(h['negative'])
            if not h.get('evidence_ids') or not h.get('dependence_groups'):raise ValueError('Missing concept evidence provenance')
            positive=set(h.get('supporting_evidence',[]));negative=set(h.get('contradicting_evidence',[]))
            if positive&negative or positive|negative!=set(h['evidence_ids']):raise ValueError('Invalid concept evidence partition')
        return True

    @classmethod
    def load(cls,path,runtime=None):
        supplied=read_json(path);expected=supplied.pop('version',None)
        try:model=cls(**supplied);model.validate(runtime)
        except (TypeError,KeyError) as error:raise ValueError('Malformed concept checkpoint') from error
        if model.version!=expected:raise ValueError('Concept checkpoint integrity mismatch')
        return model
