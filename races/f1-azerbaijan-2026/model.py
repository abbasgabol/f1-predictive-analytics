"""Regularized Plackett-Luce podium ranking with chronological evaluation.

Core library; run predict.py. Input JSON snapshots exclude target outcomes.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
DEPS = ROOT.parent / 'f1-dutch-2026' / '.deps'
if DEPS.exists():
    sys.path.insert(0, str(DEPS))
import itertools, json, hashlib
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

FEATURES = ['qualifying_quality', 'driver_last3_finish_quality',
            'driver_prior_podium_rate', 'team_last3_races_finish_quality']
L2 = 0.03  # Fixed in advance; no selection using the Italian result or validation scores.
TARGET = 15

def check_data(history, target):
    assert {r['round'] for r in history} == set(range(1, TARGET))
    assert all(r['round'] == TARGET for r in target)
    allowed = {'round','gp','driver','name','team','qualifying_position','q1','q2','q3'}
    assert all(set(r) <= allowed for r in target), 'Target contains non-qualifying columns'
    for rnd in range(1, TARGET + 1):
        rows = [r for r in history + target if r['round'] == rnd]
        assert len(rows) == 22 and len({r['driver'] for r in rows}) == 22
        assert all(1 <= r['qualifying_position'] <= 22 for r in rows)
        if rnd < TARGET:
            assert sorted(r['finish_position'] for r in rows) == list(range(1,23))

def features(field, history):
    """Whitelist features, filter strictly before each row's race; no current labels."""
    output = []
    for row in field:
        prior = [r for r in history if r['round'] < row['round']]
        driver = sorted([r for r in prior if r['driver'] == row['driver']], key=lambda r:r['round'])
        team = [r for r in prior if r['team'] == row['team']]
        recent_rounds = sorted({r['round'] for r in team})[-3:]
        team_recent = [r for r in team if r['round'] in recent_rounds]
        def quality(rows):
            return np.mean([(23-r['finish_position'])/22 for r in rows]) if rows else 0.5
        # Two pseudo-starts with field-average podium probability avoid cold-start extremes.
        podium_rate = (sum(r['finish_position'] <= 3 for r in driver) + 2*3/22)/(len(driver)+2)
        output.append([(23-row['qualifying_position'])/22,
                       quality(driver[-3:]), podium_rate, quality(team_recent)])
    return np.asarray(output, dtype=float)

def fit(history, columns=None):
    columns = list(range(len(FEATURES))) if columns is None else columns
    groups = []
    for rnd in sorted({r['round'] for r in history}):
        rows = sorted([r for r in history if r['round']==rnd], key=lambda r:r['driver'])
        x = features(rows, history)[:,columns]
        podium = sorted(range(len(rows)), key=lambda i:rows[i]['finish_position'])[:3]
        groups.append((x,podium))
    def loss_grad(w):
        loss, grad = 0., np.zeros_like(w)
        for x,podium in groups:
            remaining = list(range(len(x)))
            for winner in podium:
                scores = x[remaining] @ w
                normalizer = logsumexp(scores)
                probs = np.exp(scores-normalizer)
                loss += normalizer - x[winner] @ w
                grad += probs @ x[remaining] - x[winner]
                remaining.remove(winner)
        return loss/len(groups) + L2*np.sum(w*w), grad/len(groups) + 2*L2*w
    result = minimize(loss_grad, np.zeros(len(columns)), jac=True, method='L-BFGS-B',
                      options={'maxiter':1000,'ftol':1e-12,'gtol':1e-8})
    if not result.success:
        raise RuntimeError(result.message)
    return result.x

def distribution(x, w):
    scores = x @ w
    weights = np.exp(scores-scores.max())
    total = weights.sum()
    marginals = np.zeros((len(x),3))
    best_order, best_probability = None, -1.
    for a,b,c in itertools.permutations(range(len(x)),3):
        p = weights[a]/total * weights[b]/(total-weights[a]) * weights[c]/(total-weights[a]-weights[b])
        for slot,idx in enumerate((a,b,c)):
            marginals[idx,slot] += p
        if p > best_probability:
            best_order, best_probability = (a,b,c), p
    return marginals, best_order, best_probability
