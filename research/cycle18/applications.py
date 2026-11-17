"""Research application journal. No registry update or native output path."""
from dataclasses import asdict
from .contracts import Application, canonical, identity


class ApplicationJournal:
    def __init__(self, limit=1000):
        self.records=[];self.limit=limit

    def apply(self, fitted, *, bindings, environment, state, history, query,
              parents=None, native_execution=None):
        if len(self.records)>=self.limit:
            raise ValueError('application resource limit')
        data=fitted.json()
        if data['status']!='point_under_declared_model':
            raise ValueError('Application requires a completed reference generation')
        known={r['application']['application_id'] for r in self.records}
        if parents is not None and not set(parents)<=known:
            raise ValueError('Unknown application parent')
        generation=data['parameter_generation']['parameter_generation_id']
        app=Application('reference-application:'+str(len(self.records)+1),(generation,),canonical(bindings),
            tuple(environment),identity([state,history]),query,native_execution,
            tuple(parents) if parents is not None else None,
            'host-declared application links only; native fired-rule parents unobserved')
        record=dict(application=asdict(app),context_identity=app.context_identity,
            result_identity=fitted.scientific_identity,posterior_identity=data['posterior_identity'],
            predictive_probability=data['predictive_probability'],training_events_added=0)
        self.records.append(record)
        return record
