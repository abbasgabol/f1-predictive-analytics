"""Predict Azerbaijan with the predeclared nested chronological model-selection rule."""
import hashlib, json
import model as m
import selection as s
import numpy as np

def main():
    root=m.ROOT
    history=json.loads((root/'data/history.json').read_text())
    target=json.loads((root/'data/target_qualifying.json').read_text())
    m.check_data(history,target)
    chosen,inner=s.choose(history)
    w=s.fit(history,chosen)
    target=sorted(target,key=lambda r:r['driver'])
    x=m.features(target,history)[:,chosen['columns']]
    probabilities,order,joint=m.distribution(x,w)
    prediction=[dict(position=i+1,driver=target[idx]['driver'],name=target[idx]['name']) for i,idx in enumerate(order)]
    field=[dict(driver=r['driver'],name=r['name'],qualifying=r['qualifying_position'],
        win_probability=float(probabilities[i,0]),podium_probability=float(probabilities[i].sum())) for i,r in enumerate(target)]
    field.sort(key=lambda r:-r['podium_probability'])
    # Evaluate the fixed selection procedure without using each held-out race for its selection.
    folds=[s.predict_fold(history,rnd) for rnd in range(7,m.TARGET)]
    summary=dict(races=len(folds),mean_podium_hits=float(np.mean([r['hits'] for r in folds])),
        winners_correct=sum(r['winner_correct'] for r in folds),exact_orders=sum(r['exact_order'] for r in folds),
        mean_ordered_podium_nll=float(np.mean([r['nll'] for r in folds])))
    result=dict(cutoff='End of qualifying, 25 September 2026',event='Azerbaijan Grand Prix, Baku City Circuit, Baku',
        prediction=prediction,field=field,ordered_podium_probability=float(joint),
        selected_model=chosen,coefficients=w.tolist(),training_rounds=list(range(1,m.TARGET)),
        historical_validation=summary,inner_selection=inner,outer_folds=folds,
        probability_warning='Uncalibrated model probabilities; small historical sample.',
        target_race_labels_used=False)
    out=root/'outputs'; out.mkdir(exist_ok=True)
    (out/'prediction.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    artifact=dict(selected_model=chosen,coefficients=w.tolist(),training_races=14,training_driver_rows=len(history),
        features=[m.FEATURES[i] for i in chosen['columns']],
        selection_rule='Inner chronological NLL; prefer fewer features then stronger L2 within one standard error of best.',
        sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'data').glob('*.json')},
        implementation_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['model.py','selection.py','predict.py']})
    (out/'model.json').write_text(json.dumps(artifact,indent=2),encoding='utf-8')
    lines=['# 2026 Azerbaijan Grand Prix prediction','',
        '**Baku — cutoff: end of qualifying, 25 September 2026.**','',
        '| Predicted position | Driver |','|---|---|']
    lines += [f"| {r['position']} | {r['name']} |" for r in prediction]
    lines += ['',f"Selected model: `{chosen['name']}`. Fitted using 14 prior races (308 driver entries).",
        f'Model probability of this exact ordered podium: {joint:.2%}. Probabilities are uncalibrated.','',
        '## Driver estimates','', '| Driver | Qualifying rank | Win probability | Any podium |','|---|---:|---:|---:|']
    lines += [f"| {r['name']} | {r['qualifying']} | {r['win_probability']:.1%} | {r['podium_probability']:.1%} |" for r in field]
    lines += ['', '## Generalization safeguards','',
        '- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.',
        '- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.',
        '- No random driver-row split, target-result tuning, or target race labels.',
        '- Previous race outcomes are valid training labels. Spanish results are now historical; Azerbaijan race results were not requested or used.',
        '- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.','',
        '## Retrospective outer validation','',
        f"Eight chronological tests (rounds 7–14): average {summary['mean_podium_hits']:.2f}/3 podium drivers, {summary['winners_correct']}/8 winners, {summary['exact_orders']}/8 exact ordered podiums; mean ordered-podium NLL {summary['mean_ordered_podium_nll']:.3f}.",
        'These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Azerbaijan result has not been loaded or evaluated.',
        'With only 14 races, better future performance is not established. Do not change the rule after seeing the Azerbaijan outcome and then call it an improved Azerbaijan forecast.','',
        '## Sources and limitations','',
        '- Official Azerbaijan qualifying page: https://www.formula1.com/en/results/2026/races/1295/azerbaijan/qualifying',
        '- All 22 target entrants have qualifying classifications. Teams and driver identities are taken from this event, including driver/team changes.',
        '- The only network requests in the data builder are Azerbaijan qualifying and the preceding Spanish race result. URLs and hashes are in data/provenance.json.',
        '- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.',
        '- Historical rounds 1–13 originate in the existing local snapshots; round 14 is the official Spanish classification. NC entries use official table order for trailing finish ranks.',
        '- No Azerbaijan race telemetry, result, pit stops, actual weather, final grid, or later standings are included.',
        '- No Baku-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.','']
    (out/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'selected_model':chosen,'podium':prediction,'validation':summary},indent=2))

if __name__=='__main__': main()
