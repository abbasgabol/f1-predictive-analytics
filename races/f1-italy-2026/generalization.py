"""Nested expanding-window evaluation; no new race results or target inputs fetched.

Protocol is fixed before execution. This is retrospective development, not a new
untouched test. Original prediction/model files are never overwritten.
"""
import json, hashlib
from pathlib import Path
import model as m
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

CANDIDATES = [dict(name=f'{family}_l2_{penalty}', columns=cols, l2=penalty)
              for family,cols in [('qualifying',[0]),('form',[0,1,2,3])]
              for penalty in (0.03,0.1,0.3)]

def fit(rows, candidate):
    groups=[]
    for rnd in sorted({r['round'] for r in rows}):
        field=sorted([r for r in rows if r['round']==rnd],key=lambda r:r['driver'])
        x=m.features(field,rows)[:,candidate['columns']]
        podium=sorted(range(len(field)),key=lambda i:field[i]['finish_position'])[:3]
        groups.append((x,podium))
    def objective(w):
        loss=0.; grad=np.zeros_like(w)
        for x,podium in groups:
            remaining=list(range(len(x)))
            for idx in podium:
                scores=x[remaining]@w
                normalizer=logsumexp(scores)
                loss+=normalizer-x[idx]@w
                grad+=np.exp(scores-normalizer)@x[remaining]-x[idx]
                remaining.remove(idx)
        penalty=candidate['l2']
        return loss/len(groups)+penalty*np.sum(w*w), grad/len(groups)+2*penalty*w
    opt=minimize(objective,np.zeros(len(candidate['columns'])),jac=True,method='L-BFGS-B',
                 options={'maxiter':1000,'maxls':50,'ftol':1e-12,'gtol':1e-8})
    if not opt.success: raise RuntimeError(opt.message)
    return opt.x

def score(field, past, candidate, w):
    field=sorted(field,key=lambda r:r['driver'])
    x=m.features(field,past)[:,candidate['columns']]
    scores=x@w
    actual=sorted(range(len(field)),key=lambda i:field[i]['finish_position'])[:3]
    predicted=np.argsort(-scores,kind='stable')[:3].tolist()
    remaining=list(range(len(field))); nll=0.
    for idx in actual:
        nll+=logsumexp(scores[remaining])-scores[idx]
        remaining.remove(idx)
    return dict(nll=float(nll),hits=len(set(actual)&set(predicted)),
                winner_correct=actual[0]==predicted[0],exact_order=actual==predicted,
                prediction=[field[i]['driver'] for i in predicted])

def choose(past):
    """Only past races are accepted. Inner validation starts after three races."""
    candidates=[]
    for candidate in CANDIDATES:
        losses=[]
        for rnd in sorted({r['round'] for r in past if r['round']>=4}):
            train=[r for r in past if r['round']<rnd]
            valid=[r for r in past if r['round']==rnd]
            losses.append(score(valid,train,candidate,fit(train,candidate))['nll'])
        if len(losses)<2: raise ValueError('At least two inner validation races required')
        candidates.append(dict(candidate=candidate,mean_nll=float(np.mean(losses)),
            standard_error=float(np.std(losses,ddof=1)/np.sqrt(len(losses))),fold_losses=losses))
    best=min(candidates,key=lambda r:r['mean_nll'])
    threshold=best['mean_nll']+best['standard_error']
    eligible=[r for r in candidates if r['mean_nll']<=threshold]
    # One-standard-error heuristic: favor fewer features, then stronger shrinkage.
    chosen=min(eligible,key=lambda r:(len(r['candidate']['columns']),-r['candidate']['l2']))
    return chosen['candidate'], candidates

def predict_fold(history,rnd):
    past=[r for r in history if r['round']<rnd]
    chosen,inner=choose(past)
    w=fit(past,chosen)
    field=[r for r in history if r['round']==rnd]
    # Selection and fitting finish before evaluating the outer race labels.
    outer=score(field,past,chosen,w)
    train_losses=[score([r for r in past if r['round']==i],past,chosen,w)['nll']
                  for i in sorted({r['round'] for r in past})]
    return dict(round=rnd,selected=chosen,inner_validation=inner,
                coefficients=w.tolist(),train_nll=float(np.mean(train_losses)),**outer)

def main():
    root=m.ROOT
    protected=[root/'outputs/model.json',root/'outputs/prediction.json']
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    history=json.loads((root/'data/history.json').read_text())
    assert {r['round'] for r in history}==set(range(1,13))
    folds=[]; comparisons=[]
    for rnd in range(7,13):
        fold=predict_fold(history,rnd); folds.append(fold)
        past=[r for r in history if r['round']<rnd]
        field=[r for r in history if r['round']==rnd]
        for name,candidate in [('original',CANDIDATES[3]),('qualifying_baseline',CANDIDATES[0])]:
            comparisons.append(dict(round=rnd,method=name,**score(field,past,candidate,fit(past,candidate))))
        print(f"Round {rnd}: {fold['selected']['name']}, held-out NLL {fold['nll']:.3f}",flush=True)
    summary={}
    for method,rows in [('nested_selection',folds)]+[(name,[r for r in comparisons if r['method']==name]) for name in ['original','qualifying_baseline']]:
        summary[method]=dict(races=len(rows),mean_test_nll=float(np.mean([r['nll'] for r in rows])),
            mean_podium_hits=float(np.mean([r['hits'] for r in rows])),
            winners_correct=sum(r['winner_correct'] for r in rows),
            exact_orders=sum(r['exact_order'] for r in rows))
    chosen,inner=choose(history)
    result=dict(protocol='Nested chronological validation with one-standard-error simplicity preference',
        status='Retrospective development results; no untouched future test yet',
        candidates=CANDIDATES,summary=summary,folds=folds,comparisons=comparisons,
        mean_training_nll=float(np.mean([r['train_nll'] for r in folds])),
        next_model_candidate=chosen,next_model_coefficients=fit(history,chosen).tolist(),
        final_inner_validation=inner,history_sha256=hashlib.sha256((root/'data/history.json').read_bytes()).hexdigest())
    out=root/'generalization'; out.mkdir(exist_ok=True)
    (out/'evaluation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    text=['# Generalization review','',
        'The aim is reliable unseen-race predictions, not test scores exceeding training scores.','',
        '## Fixed evaluation protocol','',
        '- Six outer tests: rounds 7–12. Each is fitted using earlier whole races only.',
        '- Inner tests: train through round 3, predict round 4, then expand up to the race before the outer test.',
        '- Six candidates only: qualifying alone or the existing four features, each with L2 0.03, 0.1, or 0.3.',
        '- Select by ordered-podium negative log likelihood (NLL); lower is better. Within one standard error of the best inner score, prefer fewer features and then stronger regularization.',
        '- Outer test outcomes never select the model for that fold. Features use strictly previous race outcomes.',
        '- No new features, driver identity memorization, random row splits, target-result tuning, or new race-result retrieval.','',
        '## Retrospective held-out scores','',
        '| Method | Mean NLL (lower better) | Podium members / 3 | Winners | Exact ordered podiums |',
        '|---|---:|---:|---:|---:|']
    text += [f"| {name} | {r['mean_test_nll']:.3f} | {r['mean_podium_hits']:.2f} | {r['winners_correct']}/6 | {r['exact_orders']}/6 |" for name,r in summary.items()]
    text += ['',f"Nested model mean training NLL: {result['mean_training_nll']:.3f}; mean outer-test NLL: {summary['nested_selection']['mean_test_nll']:.3f}.",
        'These means concern different races and sample sizes; the gap alone cannot prove or disprove overfitting.','',
        '## Selected models by held-out race','', '| Test round | Selected candidate | Training NLL | Test NLL |','|---|---|---:|---:|']
    text += [f"| {r['round']} | {r['selected']['name']} | {r['train_nll']:.3f} | {r['nll']:.3f} |" for r in folds]
    text += ['', '## Limits and next test','',
        'These historical results have already been seen during development. Nested validation prevents within-fold leakage, but does not erase analyst exposure or create a new untouched test set.',
        'Twelve races means only 36 observed podium placements. Six outer races are too few to establish a reliable advantage. The one-standard-error rule is a simplicity heuristic; overlapping chronological folds are dependent.',
        'Stronger regularization can underfit. Do not adopt a new method solely because it wins one metric on this small retrospective comparison.',
        f"The fixed inner-selection rule proposes `{chosen['name']}` after all 12 historical races. Its coefficients are saved separately for prospective evaluation; the original forecasts are preserved.",
        'Before evaluating another race, freeze the data cutoff and selection rule. Record the forecast before viewing its outcome, then score every race without selectively skipping failures. Collect more time-ordered seasons for stronger validation, while accounting for regulation changes.',
        'The Italian race outcome supplied in chat is not ingested here. No future performance improvement or absence of overfitting is guaranteed.','']
    (out/'REPORT.md').write_text('\n'.join(text),encoding='utf-8')
    assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
