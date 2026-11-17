"""Knowledge files are data; changing a rule never changes the adapter."""
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from pln_chess.pln import TV
from .native_reasoner import Sentence, parse, render, proposition

DEFAULT_RULES = ROOT / 'knowledge/cycle15/domain_rules.metta'


def templates(path=DEFAULT_RULES):
    rules = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith(';'): continue
        node = parse(line)
        if len(node) != 3 or node[0] != 'Rule' or node[1] in rules:
            raise ValueError('Expected unique declarative Rule records')
        term = proposition(render(node[2]))
        if not term.startswith('(Implication '):
            raise ValueError('Only registered implication templates')
        rules[node[1]] = term
    if not 1 <= len(rules) <= 12: raise ValueError('Template grammar bound exceeded')
    return rules


def load_rules(checkpoint=None, *, path=DEFAULT_RULES, remove=()):
    structures = templates(path)
    if isinstance(checkpoint, (str, Path)): checkpoint = read_json(checkpoint)
    if checkpoint:
        if checkpoint['structure_hash'] != digest(structures): raise ValueError('Checkpoint structure mismatch')
        if checkpoint['version'] != digest({k:v for k,v in checkpoint.items() if k!='version'}):
            raise ValueError('Checkpoint integrity mismatch')
        if checkpoint['runtime_version'] != read_json(ROOT/'configs/runtime-lock.json')['pln']['commit']:
            raise ValueError('Checkpoint runtime mismatch')
    result=[]
    for name,term in structures.items():
        if name in remove: continue
        learned=checkpoint.get('rules',{}).get(name) if checkpoint else None
        tv=TV(**learned['truth_value']) if learned else TV(1.,.95)
        ancestry=tuple(learned['ancestry']) if learned else ()
        # Reusing a rule preserves both rule identity and training ancestry.
        stamps=('rule_'+name,)+tuple('train_'+digest(g)[:24] for g in ancestry)
        result.append(Sentence(term,tv.strength,tv.confidence,stamps,
            'learned-rule-truth-value' if learned else 'supplied-domain-rule-template',ancestry))
    return result
