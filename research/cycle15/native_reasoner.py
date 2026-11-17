"""Exact native derivation transport. Python never selects applicable rules."""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time

from pln_chess.common import ROOT, digest
from pln_chess.pln import Runtime, TV


def parse(text):
    """Parse a single data S-expression, including native variable spellings."""
    tokens = re.findall(r'\(|\)|[^\s()]+', text)
    index = 0
    def read():
        nonlocal index
        if index >= len(tokens):
            raise ValueError('Truncated expression')
        token = tokens[index]; index += 1
        if token == '(':
            result = []
            while index < len(tokens) and tokens[index] != ')':
                result.append(read())
            if index == len(tokens):
                raise ValueError('Missing closing parenthesis')
            index += 1
            return result
        if token == ')':
            raise ValueError('Unexpected closing parenthesis')
        return token
    result = read()
    if index != len(tokens):
        raise ValueError('Multiple expressions')
    return result


def render(value):
    return '(' + ' '.join(map(render, value)) + ')' if isinstance(value, (list, tuple)) else str(value)


def alpha_key(term):
    """Telemetry identity only: ignore native variable renaming, preserve roles."""
    names={}
    def walk(value):
        if isinstance(value,list):return [walk(v) for v in value]
        if value.startswith('$'):
            if value not in names:names[value]='$v'+str(len(names))
            return names[value]
        return value
    return render(walk(parse(term)))


def proposition(text):
    node = parse(text)
    forbidden = {'=', '!', 'progn', 'case', 'let', 'let*', 'if', 'collapse', 'superpose',
                 'empty', 'STV', 'Sentence', 'stv', 'get-atoms', 'match', 'eval', '|-'}
    def check(value):
        if isinstance(value, list):
            if not value or not isinstance(value[0], str):
                raise ValueError('Proposition must have a symbolic head')
            for child in value: check(child)
        elif (not re.fullmatch(r'\$?[A-Za-z_][A-Za-z0-9_-]*|-?[0-9]+', value)
              or value in forbidden or value.startswith(('Truth_', 'PLN', 'import'))):
            raise ValueError('Only declarative proposition data is accepted')
    check(node)
    return render(node)


@dataclass(frozen=True)
class Sentence:
    term: str
    strength: float = 1.0
    confidence: float = .99
    stamps: tuple[str, ...] = ()
    origin: str = 'environmental-observation'
    ancestry: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'term', proposition(self.term))
        TV(self.strength, self.confidence)
        if not self.stamps or len(set(self.stamps)) != len(self.stamps):
            raise ValueError('Nonempty distinct evidence stamps are required')
        if any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', stamp) for stamp in self.stamps):
            raise ValueError('Unsafe evidence stamp')
        if self.origin not in ('environmental-observation', 'supplied-domain-rule-template',
                               'learned-rule-truth-value', 'stage-a-imported-premise', 'audit-input'):
            raise ValueError('Unregistered input origin')

    def metta(self):
        return f'(Sentence ({self.term} {TV(self.strength, self.confidence).metta()}) ({" ".join(self.stamps)}))'


@dataclass(frozen=True)
class Budgets:
    steps: int = 24
    tasks: int = 64
    beliefs: int = 128
    timeout: float = 10.0

    def __post_init__(self):
        if any(type(v) is not int or not 0 <= v <= 512 for v in (self.steps, self.tasks, self.beliefs)):
            raise ValueError('Native integer budgets must lie in [0,512]')
        if not self.tasks or not self.beliefs:
            raise ValueError('Zero queue capacities recurse indefinitely in the pinned library')
        if not math.isfinite(self.timeout) or not 0 < self.timeout <= 60:
            raise ValueError('Invalid timeout')


def unpack_sentence(node):
    if not isinstance(node, list) or len(node) != 3 or node[0] != 'Sentence':
        raise ValueError('Malformed native sentence')
    term, tv = node[1]
    if len(tv) != 3 or tv[0] != 'stv':
        raise ValueError('Malformed native truth value')
    value = TV(float(tv[1]), float(tv[2]))
    return dict(term=render(term), **value.json(), stamps=node[2])


class NativeReasoner:
    def __init__(self, runtime=None):
        self.runtime = runtime or Runtime()

    def execute_program(self, program, timeout=10):
        """Retain failures, partial output and per-process GNU time measurements."""
        self.runtime.verify()
        start = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix='c15-native-') as directory:
            directory = Path(directory)
            path = directory / 'input.metta'; path.write_text(program)
            timing = directory / 'resources.txt'
            argv = ['/usr/bin/time', '-v', '-o', str(timing), 'sh', str(self.runtime.runner), str(path), '--silent']
            with (directory / 'stdout').open('w') as stdout, (directory / 'stderr').open('w') as stderr:
                process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr, start_new_session=True)
                timed_out = False
                try: process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            output = (directory / 'stdout').read_text(errors='replace')
            errors = (directory / 'stderr').read_text(errors='replace')
            resources = timing.read_text() if timing.exists() else ''
        memory = re.search(r'Maximum resident set size \(kbytes\): (\d+)', resources)
        cpu = re.findall(r'(?:User|System) time \(seconds\): ([\d.]+)', resources)
        incomplete = timed_out or process.returncode != 0 or bool(re.search(r'ERROR|typecheck error', errors, re.I))
        return dict(program=program, program_sha256=hashlib.sha256(program.encode()).hexdigest(),
            stdout=output, stderr=errors, returncode=process.returncode, timed_out=timed_out,
            incomplete=incomplete, wall_seconds=time.perf_counter()-start,
            peak_rss_kib=int(memory[1]) if memory else None, cpu_seconds=sum(map(float, cpu)) if cpu else None,
            resource_raw=resources, output_bytes=len(output.encode())+len(errors.encode()),
            runtime=self.runtime.manifest, native_processes=1,
            execution_trace_scope='Directly observed SELECTED tasks; no fired-rule tree')

    def infer(self, facts, rules, query, *, contrary=None, budgets=None, mode='derive',
              marginals=None, tasks=None):
        budgets = budgets or Budgets()
        if mode not in ('derive', 'query'):
            raise ValueError('Unknown native API')
        query = proposition(query)
        contrary = proposition(contrary) if contrary else None
        beliefs = [*facts, *rules]
        tasks = beliefs if tasks is None else list(tasks)
        if len(beliefs) > 256 or len(tasks) > 256:
            raise ValueError('Initial knowledge base exceeds registered input bound')
        declarations = ''
        for term, tv in (marginals or {}).items():
            declarations += f'(= (STV {proposition(term)}) {TV(*tv).metta()})\n'
        kb = '(' + ' '.join(sentence.metta() for sentence in beliefs) + ')'
        initial = '(' + ' '.join(sentence.metta() for sentence in tasks) + ')'
        prefix = f'!(import! &self "{self.runtime.library}")\n' + declarations
        prefix += f'(= (c15beliefs) {kb})\n(= (c15tasks) {initial})\n'
        suffix = f'{budgets.steps} {budgets.tasks} {budgets.beliefs}'
        if mode == 'query':
            body = f'!(println! (C15ANSWER (PLN.Query (c15tasks) (c15beliefs) {query} {suffix})))\n'
            if contrary:
                body += f'!(println! (C15CONTRARY (PLN.Query (c15tasks) (c15beliefs) {contrary} {suffix})))\n'
        else:
            # Exact native Query selection expression on the one returned KB.
            # The host neither unifies schemas nor chooses an inference sequence.
            def select(term):
                return ('(BestConfidenceCandidate (collapse (let (Sentence ($Term $TV) $Ev) '
                        '(superpose $retained) (case (== $Term ' + term + ') ((True ($TV $Ev)))))))')
            prints = f'(println! (C15ANSWER {select(query)}))'
            if contrary: prints += f' (println! (C15CONTRARY {select(contrary)}))'
            body = (f'!(let ($remaining $retained) (PLN.Derive (c15tasks) (c15beliefs) 1 {suffix}) '
                    f'(progn (println! (C15STATE $remaining $retained)) {prints}))\n')
        receipt = self.execute_program(prefix + body, budgets.timeout)
        selected, retained, remaining = [], [], []
        answers = {'answer': None, 'contrary': None}
        counts = {'C15ANSWER': 0, 'C15CONTRARY': 0, 'C15STATE': 0}
        try:
            for line in receipt['stdout'].splitlines():
                if line.startswith('(SELECTED '): selected.append(unpack_sentence(parse(line)[1]))
                elif line.startswith('(C15STATE '):
                    node = parse(line); counts['C15STATE'] += 1
                    remaining = [unpack_sentence(value) for value in node[1]]
                    retained = [unpack_sentence(value) for value in node[2]]
                elif line.startswith(('(C15ANSWER ', '(C15CONTRARY ')):
                    marker, result = parse(line); counts[marker] += 1
                    if result:
                        tv, stamps = result
                        answers['answer' if marker == 'C15ANSWER' else 'contrary'] = dict(
                            **TV(float(tv[1]), float(tv[2])).json(), stamps=stamps)
            expected = {'C15ANSWER': 1, 'C15CONTRARY': int(contrary is not None), 'C15STATE': int(mode == 'derive')}
            if counts != expected:
                raise ValueError(f'Ambiguous or missing native result: {counts}')
        except (ValueError, TypeError, IndexError) as error:
            receipt.update(incomplete=True, parse_error=str(error))
        initial_terms = {alpha_key(sentence.term) for sentence in beliefs}
        derived = [s for s in retained if alpha_key(s['term']) not in initial_terms]
        def supported(channel):
            return channel is not None and channel['strength'] >= .6 and channel['confidence'] >= .1
        positive, negative = supported(answers['answer']), supported(answers['contrary'])
        classification = ('incomplete' if receipt['incomplete'] else 'conflicting' if positive and negative
                          else 'supported-positive' if positive else 'supported-negative' if negative else 'unknown')
        return dict(query=query, contrary_query=contrary, **answers, classification=classification,
            incomplete=receipt['incomplete'], facts=[asdict(s) for s in facts], rules=[asdict(s) for s in rules],
            budgets=asdict(budgets), api=mode, marginals=marginals or {},
            selected=selected, retained=retained, remaining=remaining,
            usage=dict(initial_tasks=len(tasks), initial_beliefs=len(beliefs), selected_tasks=len(selected),
                retained_tasks=len(remaining) if mode == 'derive' else None,
                retained_beliefs=len(retained) if mode == 'derive' else None,
                derived_statements=len(derived) if mode == 'derive' else None,
                repeated_selected_terms=len(selected)-len({s['term'] for s in selected}),
                native_processes=1, derivation_calls=2 if mode == 'query' and contrary else 1,
                host_grounded_instances=0, native_schema_instances='Not completely observable in native trace'),
            grounding_mode='native-schema-binding' if any('$' in s.term for s in rules) else 'ground-instance-native-inference',
            completion=('incomplete execution' if receipt['incomplete'] else 'task queue exhausted' if mode == 'derive' and not remaining
                        else 'bounded run; no completeness claim'),
            proof_status='native-selected-tasks-and-returned-evidence-stamps; no reconstructed fired-rule tree',
            receipt=receipt)


def save_result(result, directory):
    """Immutable content-bound files; large transcripts stay outside Git."""
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    identifier = hashlib.sha256(raw.encode()).hexdigest()
    path = directory / (identifier + '.json')
    if not path.exists(): path.write_text(raw)
    return dict(path=str(path), sha256=identifier, bytes=len(raw.encode()))
