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
