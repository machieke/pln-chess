"""Immutable identities, admission and generation contracts. No native imports."""
from dataclasses import dataclass, asdict
from enum import StrEnum
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def identity(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


class Kind(StrEnum):
    ENVIRONMENT = 'direct_environmental_observation'
    EVALUATION = 'evaluation_generated_annotation'
    DERIVED = 'deterministic_derived_annotation'
    SYNTHETIC = 'synthetic_intervention'
    UNKNOWN = 'unknown_missing_observation'
    SUPERSEDED = 'superseded_observation_version'


@dataclass(frozen=True)
class Observation:
    event_id: str
    payload_hash: str
    source_artifact_path: str | None
    source_artifact_hash: str | None
    source_locator: str | None
    source_episode_id: str
    ancestry_groups: tuple[str, ...]
    observed_variables_json: str
    observation_kind: Kind
    measurement_or_label_method: str
    parent_event_ids: tuple[str, ...]
    admission_status: str
    exclusion_reason: str | None
    generation_or_supersession_identity: str
    supersedes: str | None = None
    historical_measurement_time: str | None = None

    def __post_init__(self):
        payload = json.loads(self.observed_variables_json)
        if identity(payload) != self.payload_hash:
            raise ValueError('Payload integrity mismatch')
        if not self.event_id or not self.ancestry_groups or len(set(self.ancestry_groups)) != len(self.ancestry_groups):
            raise ValueError('Missing/duplicate event or ancestry identity')
        if not isinstance(self.observation_kind, Kind):
            raise ValueError('Unknown observation kind; predictions are not observations')
        if self.admission_status not in ('admitted', 'excluded', 'context'):
            raise ValueError('Invalid admission')
        if self.admission_status == 'excluded' and not self.exclusion_reason:
            raise ValueError('Exclusion requires reason')
        if self.event_id in self.parent_event_ids or self.event_id == self.supersedes:
            raise ValueError('Event cannot parent/supersede itself')

    @property
    def payload(self):
        return json.loads(self.observed_variables_json)  # callers receive a copy

    def json(self):
        result = asdict(self)
        result['observed_variables'] = result.pop('observed_variables_json')
        result['observed_variables'] = json.loads(result['observed_variables'])
        return result


def observation(event_id, payload, *, episode, groups, kind, method, parents=(),
                admission='context', exclusion=None, source=None, locator=None,
                generation='cycle18-mapping-v1', supersedes=None):
    return Observation(event_id, identity(payload), source[0] if source else None,
        source[1] if source else None, locator, episode, tuple(groups), canonical(payload),
        kind, method, tuple(parents), admission, exclusion, generation, supersedes)


class Registry:
    """Append-only records; explicit supersession changes only the active view."""
    def __init__(self):
        self._records = {}
        self._superseded = set()

    def register(self, event):
        if not isinstance(event, Observation):
            raise TypeError('Only external/mapped observations, never predictions or applications')
        old = self._records.get(event.event_id)
        if old is not None:
            if old != event:
                raise ValueError('Same event ID with changed content or provenance')
            return False
        for parent in (*event.parent_event_ids, *((event.supersedes,) if event.supersedes else ())):
            if parent not in self._records:
                raise ValueError('Unknown parent/superseded event')
        if event.supersedes:
            old = self._records[event.supersedes]
            if event.supersedes in self._superseded or old.source_episode_id != event.source_episode_id:
                raise ValueError('Invalid supersession lineage')
            self._superseded.add(event.supersedes)
        self._records[event.event_id] = event
        return True

    def get(self, event_id):
        return self._records[event_id]

    def active(self):
        return tuple(self._records[k] for k in sorted(self._records) if k not in self._superseded)

    def all(self):
        return tuple(self._records[k] for k in sorted(self._records))

    @property
    def scientific_identity(self):
        return identity([e.json() for e in self.active()])


@dataclass(frozen=True)
class ParameterGeneration:
    schema_id: str
    parameter_generation_id: str
    admitted_event_ids: tuple[str, ...]
    excluded_event_ids: tuple[str, ...]
    training_source_groups: tuple[str, ...]
    learner_identity: str
    model_assumptions_id: str
    uncertainty_representation: str
    prior_generation_id: str | None
    native_checkpoint_reference: str | None
    generation_content_hash: str
    namespace: str

    @classmethod
    def create(cls, *, namespace, schema_id, events, excluded, groups, learner,
               assumptions, uncertainty, prior=None, checkpoint=None):
        if namespace not in ('native-original', 'reference-only'):
            raise ValueError('Unknown generation namespace')
        if namespace == 'reference-only' and checkpoint is not None:
            raise ValueError('Reference generations cannot construct native checkpoints')
        content = dict(namespace=namespace, schema_id=schema_id,
            admitted_event_ids=tuple(sorted(set(events))), excluded_event_ids=tuple(sorted(set(excluded))),
            training_source_groups=tuple(sorted(set(groups))), learner_identity=learner,
            model_assumptions_id=assumptions, uncertainty_representation=uncertainty,
            prior_generation_id=prior, native_checkpoint_reference=checkpoint)
        h = identity(content)
        return cls(parameter_generation_id=namespace+':'+h, generation_content_hash=h, **content)


@dataclass(frozen=True)
class Application:
    application_id: str
    parameter_generation_refs: tuple[str, ...]
    entity_bindings_json: str
    environmental_event_refs: tuple[str, ...]
    state_and_history_identity: str
    query: str
    native_execution_reference: str | None
    observed_parent_refs: tuple[str, ...] | None
    parent_observability: str

    @property
    def context_identity(self):
        d = asdict(self); d.pop('application_id')
        return identity(d)
