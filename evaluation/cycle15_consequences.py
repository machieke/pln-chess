"""Matched C15 endpoints. Reference labels stay outside native inference."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import random

from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.domain import Piece,Position,square_name
from pln_chess.cycle11.fields.inference import infer_queries
from pln_chess.cycle11.fields.model import FieldModel
from research.cycle15.native_reasoner import NativeReasoner,Sentence,save_result
from research.cycle15.queries import infer_state
from .cycle15_corpus import registration,episode,reference


def compact(result,out):
    proof=save_result(result,out/'raw')
    return dict(classification=result['classification'],answer=result['answer'],contrary=result['contrary'],
        incomplete=result['incomplete'],query=result['query'],grounding_mode=result['grounding_mode'],
        usage=result['usage'],wall_seconds=result['receipt']['wall_seconds'],
        peak_rss_kib=result['receipt']['peak_rss_kib'],proof=proof)


def matched_field(state,query,reasoner,model,out):
    position=Position(tuple(Piece(p['id'],p['kind'].title(),p['owner'].title(),tuple(p['cell'])) for p in state['pieces']),
        state['actor'].title(),unknown_squares=tuple(tuple(c) for c in state['unknown']))
    byid={p['id']:p for p in state['pieces']};a=byid.get(query['attacker']);t=byid.get(query['target'])
    if not a or not t:return dict(classification='unsupported',reason='specified entity absent'),dict(classification='unsupported',reason='specified entity absent')
    current=infer_queries([dict(id=state['id'],position=position,source_square=square_name(a['cell']),
        target_square=square_name(t['cell']),families=['attack'])],model,runtime=reasoner.runtime)
    record=current['relations'][0]
    a_result=dict(classification={'supported':'supported-positive','contradicted':'supported-negative'}.get(record['classification'],record['classification']),
        raw_stv=record['raw_stv'],wall_seconds=current['elapsed_seconds'],proof=save_result(current,out/'raw'),
        rule_id=record['rule_id'],model_version=model.version)
    hypothesis=model.hypotheses.get(record['rule_id'])
    if not hypothesis or not record['observation']['complete']:
        return a_result,dict(classification='unknown',reason='same conditional absent or observation incomplete',native_processes=0)
    facts=[Sentence('ObservedConditionalContext',1.,.99,('context_'+digest([state,query])[:24],),'audit-input')]
    stamps=tuple('legacy_'+digest(g)[:24] for g in hypothesis['dependence_groups'])
    rules=[]
    for channel,target in (('positive','AttackTarget'),('negative','(Not AttackTarget)')):
        tv=hypothesis[channel]
        rules.append(Sentence(f'(Implication ObservedConditionalContext {target})',tv['strength'],tv['confidence'],
            ('conditional_'+channel,)+stamps,'learned-rule-truth-value',tuple(hypothesis['dependence_groups'])))
    result=reasoner.infer(facts,rules,'AttackTarget',contrary='(Not AttackTarget)')
    # Frozen A selects max-confidence positive versus negation-eliminated
    # negative support. Report the identical raw choice and both channels in B.
    chosen=result['answer']
    if not result['incomplete'] and chosen and chosen['confidence']>=.25:
        classification='supported-positive' if chosen['strength']>=.8 else 'supported-negative' if chosen['strength']<=.2 else 'unknown'
    else:classification='incomplete' if result['incomplete'] else 'unknown'
    b_result=compact(result,out);b_result.update(classification=classification,
        conditional_scope='Exact frozen field conditional knowledge; descriptor construction remains the old baseline',
        raw_stv={k:chosen[k] for k in ('strength','confidence')} if chosen else None)
    return a_result,b_result


def metrics(rows,arm):
    classified=[];counts=Counter();positives=negatives=positive_correct=negative_answered=0
    for row in rows:
        label=row['reference']['label'];answer=row['arms'][arm]['classification'];counts[answer]+=1
        if label is True:positives+=1
        if label is False:negatives+=1
        if answer in ('supported-positive','supported-negative') and label is not None:
            correct=(answer=='supported-positive')==label
            classified.append(correct)
            positive_correct+=int(label is True and correct)
            negative_answered+=int(label is False)
    return dict(observations=len(rows),roots=len({r['root'] for r in rows}),outcomes=dict(counts),
        correct=sum(classified),incorrect=len(classified)-sum(classified),classified=len(classified),
        classified_accuracy=sum(classified)/len(classified) if classified else None,
        reference_positives=positives,reference_negatives=negatives,
        positive_recall_including_abstention=positive_correct/positives if positives else None,
        negative_coverage=negative_answered/negatives if negatives else None)


def intervals(rows,arm):
    groups={root:[r for r in rows if r['root']==root] for root in sorted({r['root'] for r in rows})}
    rng=random.Random(15);keys=list(groups);values=[]
    for _ in range(1000):
        sampled=[r for key in rng.choices(keys,k=len(keys)) for r in groups[key]]
        value=metrics(sampled,arm)['classified_accuracy']
        if value is not None:values.append(value)
    values.sort()
    return dict(method='synthetic-root cluster bootstrap; conditional on designed panel, not natural games',
        draws=1000,defined=len(values),accuracy_95=[values[int(.025*len(values))],values[min(len(values)-1,int(.975*len(values)))]] if values else None)


def run(out,checkpoint,workers=2,splits=('development','test')):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    model=read_json(checkpoint);roots=[r for r in registration() if r['split'] in splits]
    write_json(out/'registered-roots.json',roots)
    def worker(root):
        target=out/'roots'/f"{root['id']}.json"
        if target.exists():
            stored=read_json(target)
            if stored['checkpoint_version']!=model['version']:raise ValueError('Cannot resume a different model')
            return stored['rows']
        reasoner=NativeReasoner();field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',reasoner.runtime)
        e=episode(root);rows=[]
        for endpoint,state in (('before',e['state']),('after',e['after'])):
            arms={}
            arms['A'],arms['B']=matched_field(state,e['query'],reasoner,field,out)
            arms['C']=compact(infer_state(state,e['query'],reasoner=reasoner),out)
            arms['D']=compact(infer_state(state,e['query'],model,reasoner=reasoner),out)
            # References are generated after all predictions and never passed in.
            rows.append(dict(root=root['id'],split=root['split'],family=root['family'],endpoint=endpoint,
                state=state,query=e['query'],reference=reference(state,e['query']),arms=arms))
        write_json(target,dict(checkpoint_version=model['version'],rows=rows))
        print('ENDPOINTS',root['split'],root['id'],[(r['endpoint'],{k:v['classification'] for k,v in r['arms'].items()}) for r in rows],flush=True)
        return rows
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows=[row for group in pool.map(worker,roots) for row in group]
    summary={split:{arm:{**metrics([r for r in rows if r['split']==split],arm),
        'uncertainty':intervals([r for r in rows if r['split']==split],arm)} for arm in 'ABCD'} for split in splits}
    summary['matched_A_B']=dict(rows=len(rows),classification_mismatches=sum(r['arms']['A']['classification']!=r['arms']['B']['classification'] for r in rows),
        note='B exposes both native channels; final matched classification uses the frozen A thresholds and native confidence selection')
    write_json(out/'results.json',rows);write_json(out/'summary.json',summary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--checkpoint',required=True)
    parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args();run(args.out,args.checkpoint,args.workers)
