from __future__ import annotations
from dataclasses import dataclass, asdict
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from pln_chess.common import ROOT, read_json

class NativeError(RuntimeError):
    pass

@dataclass(frozen=True)
class TV:
    strength: float
    confidence: float

    def __post_init__(self):
        if not all(math.isfinite(x) and 0 <= x <= 1 for x in (self.strength, self.confidence)):
            raise NativeError(f"Invalid native STV: {self}")

    def metta(self):
        return f"(stv {float(self.strength)!r} {float(self.confidence)!r})"

    def json(self):
        return {'strength': self.strength, 'confidence': self.confidence}

    @classmethod
    def from_json(cls, value):
        return cls(**value)

UNKNOWN = TV(0.5, 0.0)  # Explicit absent-evidence prior, never a negative conclusion.

class Runtime:
    """Execute untouched upstream MeTTa through pinned PeTTa. No Python TV math.

    Batches are deterministic ground schedules of native operators, not an
    alternative inference calculus. Runtime errors never fall back to Python.
    """
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.manifest = read_json(ROOT / "configs/runtime-lock.json")
        self.library = ROOT / "vendor/pln/lib_pln.metta"
        self.runner = ROOT / ".runtime/petta/run.sh"
        self.elapsed = 0.0
        self.invocations = 0
        self.verify()

    def verify(self):
        import hashlib
        if not self.runner.exists() or not shutil.which("swipl"):
            raise NativeError("Native runtime unavailable. Run bash scripts/bootstrap.sh; requires SWI-Prolog 10.0.1.")
        if hashlib.sha256(self.library.read_bytes()).hexdigest() != self.manifest["pln"]["sha256"]:
            raise NativeError("PLN source hash differs from the audited runtime lock")
        for relative, expected in self.manifest["petta"]["files"].items():
            path = self.runner.parent / relative
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise NativeError(f"PeTTa runtime differs from lock: {relative}")
        version = subprocess.check_output(["swipl", "--version"], text=True).strip()
        if version != self.manifest["swipl"]:
            raise NativeError(f"SWI version mismatch: expected {self.manifest['swipl']}, got {version}")

    def execute(self, body):
        source = f'!(import! &self "{self.library}")\n' + body
        started = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="pln-chess-") as tmp:
            path = Path(tmp) / "query.metta"
            path.write_text(source)
            try:
                result = subprocess.run(["sh", str(self.runner), str(path), "--silent"],
                                        capture_output=True, text=True, timeout=self.timeout,
                                        cwd=ROOT)
            except subprocess.TimeoutExpired as error:
                raise NativeError(f"Native inference timed out after {self.timeout}s") from error
        self.elapsed += time.perf_counter() - started
        if result.returncode or re.search(r"ERROR|typecheck error", result.stderr, re.I):
            raise NativeError(f"PeTTa failed: {result.stderr[-2000:]}\n{result.stdout[-500:]}")
        return result.stdout

    def batch(self, nodes):
        """nodes: [(identifier, expression)] with optional earlier (node-name) refs."""
        if not nodes:
            return {}
        if len(nodes) > 400:
            # Bound PeTTa's dynamic-definition compilation cost. References across
            # chunks are substituted with already returned raw native TVs only.
            all_values = {}
            started = time.perf_counter()
            original_timeout = self.timeout
            try:
                for start in range(0, len(nodes), 400):
                    remaining = original_timeout - (time.perf_counter() - started)
                    if remaining <= 0:
                        raise NativeError(f"Native batch exceeded {original_timeout}s total budget")
                    self.timeout = remaining
                    chunk = []
                    for name, expr in nodes[start:start+400]:
                        expr = re.sub(r"\(([a-zA-Z][a-zA-Z0-9_-]*)\)",
                                      lambda m: all_values[m[1]].metta() if m[1] in all_values else m[0], expr)
                        chunk.append((name, expr))
                    all_values.update(self.batch(chunk))
            finally:
                self.timeout = original_timeout
            return all_values
        for name, _ in nodes:
            if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name):
                raise ValueError("Unsafe native node identifier")
        # Bind each returned native TV once in a native let*. This preserves
        # dependencies without dynamically recompiling one function per node.
        bindings = []
        available = set()
        for name, expr in nodes:
            expr = re.sub(r"\$([a-zA-Z][a-zA-Z0-9_-]*)", lambda m: "$local_" + name + "_" + m[1], expr)
            expr = re.sub(r"\(([a-zA-Z][a-zA-Z0-9_-]*)\)",
                          lambda m: "$" + m[1] if m[1] in available else m[0], expr)
            bindings.append(f"(${name} {expr})")
            available.add(name)
        prints = " ".join(f"(println! (RESULT {name} ${name}))" for name, _ in nodes)
        body = "!(let* (" + " ".join(bindings) + ") (progn " + prints + "))"
        output = self.execute(body)
        matches = re.findall(r"^\(RESULT ([\w-]+) \(stv ([^ ]+) ([^)]+)\)\)$", output, re.M)
        values = {}
        for name, strength, confidence in matches:
            if name in values:
                raise NativeError(f"Ambiguous native derivation: {name}")
            values[name] = TV(float(strength), float(confidence))
        missing = set(name for name, _ in nodes) - values.keys()
        if missing:
            raise NativeError(f"No native result for {sorted(missing)[:5]}; output: {output[-1000:]}")
        self.invocations += len(nodes)
        return values

    def revision(self, left, right):
        if left.confidence == 1 or right.confidence == 1:
            raise NativeError("Native revision is undefined for confidence=1; use finite evidence")
        return self.batch([("revision", f"(let ($a $t) (|- (Belief {left.metta()}) (Belief {right.metta()})) $t)")])["revision"]

    @property
    def version(self):
        return self.manifest["pln"]["commit"]
