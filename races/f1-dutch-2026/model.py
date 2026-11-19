"""Regularized Plackett-Luce podium ranking with chronological evaluation.

Run: python model.py. Input JSON snapshots are offline and exclude target outcomes.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
if (ROOT / '.deps').exists():
    sys.path.insert(0, str(ROOT / '.deps'))
import itertools, json, hashlib
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

FEATURES = ['qualifying_quality', 'driver_last3_finish_quality',
            'driver_prior_podium_rate', 'team_last3_races_finish_quality']
L2 = 0.03  # Fixed in advance; no selection using the Dutch result or validation scores.
TARGET = 12

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

def evaluate(history):
    records=[]
    # Fixed protocol: train on rounds 1-6, test 7; expand one race at a time through 11.
    for rnd in range(7,12):
        past=[r for r in history if r['round'] < rnd]
        field=sorted([r for r in history if r['round']==rnd],key=lambda r:r['driver'])
        x=features(field,past)
        actual=[r['driver'] for r in sorted(field,key=lambda r:r['finish_position'])[:3]]
        for method,cols in [('form_and_qualifying',list(range(4))),('qualifying_only',[0])]:
            w=fit(past,cols)
            probs,order,joint=distribution(x[:,cols],w)
            pred=[field[i]['driver'] for i in order]
            actual_idx=[next(i for i,r in enumerate(field) if r['driver']==d) for d in actual]
            scores=x[:,cols]@w
            remaining=list(range(len(field)))
            nll=0.
            for idx in actual_idx:
                nll += logsumexp(scores[remaining])-scores[idx]
                remaining.remove(idx)
            records.append(dict(round=rnd,gp=field[0]['gp'],method=method,
                prediction=pred,actual=actual,podium_hits=len(set(pred)&set(actual)),
                winner_correct=pred[0]==actual[0],exact_order=pred==actual,
                ordered_podium_nll=float(nll)))
    return records

def main():
    history=json.loads((ROOT/'data/history.json').read_text())
    target=json.loads((ROOT/'data/target_qualifying.json').read_text())
    check_data(history,target)
    validation=evaluate(history)
    w=fit(history)
    target=sorted(target,key=lambda r:r['driver'])
    x=features(target,history)
    probs,order,joint=distribution(x,w)
    prediction=[dict(position=i+1,driver=target[idx]['driver'],name=target[idx]['name']) for i,idx in enumerate(order)]
    field=[]
    for idx in np.argsort(-(probs.sum(axis=1))):
        r=target[idx]
        field.append(dict(driver=r['driver'],name=r['name'],team=r['team'],
            qualifying_position=r['qualifying_position'],p1=float(probs[idx,0]),
            p2=float(probs[idx,1]),p3=float(probs[idx,2]),podium=float(probs[idx].sum()),
            features=dict(zip(FEATURES,x[idx].tolist()))))
    summary={}
    for method in ['form_and_qualifying','qualifying_only']:
        rows=[r for r in validation if r['method']==method]
        summary[method]={'races':len(rows),'mean_podium_hits':float(np.mean([r['podium_hits'] for r in rows])),
            'winner_correct':sum(r['winner_correct'] for r in rows),
            'exact_order_correct':sum(r['exact_order'] for r in rows),
            'mean_ordered_podium_nll':float(np.mean([r['ordered_podium_nll'] for r in rows]))}
    result={'cutoff':'End of qualifying on 22 August 2026',
        'prediction':prediction,'ordered_podium_probability':float(joint),
        'probability_warning':'Model-implied probabilities, not externally calibrated; only 11 training races.',
        'field':field,'validation_summary':summary,'validation':validation}
    out=ROOT/'outputs'; out.mkdir(exist_ok=True)
    (out/'prediction.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    artifact={'model':'L2 regularized Plackett-Luce, top-three likelihood',
        'features':FEATURES,'coefficients':w.tolist(),'l2':L2,'training_rounds':list(range(1,12)),
        'training_races':11,'training_driver_rows':len(history),
        'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.json')}}
    (out/'model.json').write_text(json.dumps(artifact,indent=2),encoding='utf-8')
    lines=['# 2026 Dutch Grand Prix prediction','',
        '**Cutoff: end of qualifying, 22 August 2026. Dutch race outcomes are excluded.**','',
        '| Predicted place | Driver |','|---|---|']
    lines += [f"| {r['position']} | {r['name']} |" for r in prediction]
    lines += ['',f'Model-implied probability of this exact ordered podium: {joint:.1%}.',
        'Probabilities are not independently calibrated. This is a small-data forecast, not a guarantee.','',
        '## Driver estimates','', '| Driver | Qualifying | Win | Second | Third | Any podium |',
        '|---|---:|---:|---:|---:|---:|']
    lines += [f"| {r['name']} | {r['qualifying_position']} | {r['p1']:.1%} | {r['p2']:.1%} | {r['p3']:.1%} | {r['podium']:.1%} |" for r in field]
    lines += ['', '## Walk-forward validation','',
        'Each of rounds 7–11 is predicted using only earlier races. All drivers from a race stay together.',
        'Hyperparameters and the evaluation window are fixed, not chosen by validation performance.','',
        '| Model | Podium drivers correct (of 3), average | Winners correct | Exact ordered podiums | Mean podium negative log likelihood |',
        '|---|---:|---:|---:|---:|']
    lines += [f"| {m} | {s['mean_podium_hits']:.2f} | {s['winner_correct']}/5 | {s['exact_order_correct']}/5 | {s['mean_ordered_podium_nll']:.3f} |" for m,s in summary.items()]
    lines += ['', '## Data and limitations','',
        '- Trained on 242 driver entries from the 11 races before the Dutch GP. Only 33 podium placements inform the ranking likelihood.',
        '- Qualifying classifications: official Formula 1 qualifying pages, recorded in data/provenance.json.',
        '- Historical finishing positions: existing local f1_2026_final_dataset.xlsx, rounds 1–11. These labels were not all independently verified.',
        '- Features: qualifying rank, driver last-three-race finishing form, smoothed prior podium rate, and team form over its last three races.',
        '- Drivers omitted from historical qualifying tables receive tied rank 22; historical field membership comes from the local dataset. A new driver uses neutral form and a field-average prior.',
        '- No current-race finishing position, points, status, pit stops, fastest laps, actual race weather, final grid, or current/end-season standings enter the feature matrix.',
        '- Previous race results are valid historical predictors. Current race results are used only as labels for training and historical validation.',
        '- Qualifying tables retrieved retrospectively can include later classification corrections. No archived as-of timestamps are available, so the exact historical publication state is not certified.',
        '- No Dutch race-result endpoint was requested. The model does not read any Dutch race label.',
        '- No track-history, practice pace, sprint, weather forecast, or penalty features are included. Eleven races and five evaluation races are too few to establish robust generalization or calibration.',
        '- The exported coefficients plus feature definitions reproduce the prediction. No target-result scoring is performed.','']
    (out/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'podium':prediction,'validation':summary},indent=2))

if __name__=='__main__':
    main()
