"""Post-race evaluation using user-supplied results; never trains or edits snapshots."""
import hashlib
import itertools
import json
import math
import model as m
import numpy as np

def main():
    protected = [m.ROOT/'outputs/model.json', m.ROOT/'outputs/prediction.json',
                 *sorted((m.ROOT/'data').glob('*.json'))]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    forecast = json.loads((m.ROOT/'outputs/prediction.json').read_text())
    fitted = json.loads((m.ROOT/'outputs/model.json').read_text())
    actual = ['NOR', 'ANT', 'RUS']  # Supplied by the user after the forecast.
    predicted = [r['driver'] for r in forecast['prediction']]
    field = forecast['field']
    coefficients = np.array(fitted['coefficients'])
    contributions = {r['driver']: np.array([r['features'][f] for f in fitted['features']])*coefficients for r in field}
    scores = {d: float(c.sum()) for d,c in contributions.items()}
    weights = {d: math.exp(v-max(scores.values())) for d,v in scores.items()}
    def probability(order):
        remaining = sum(weights.values())
        p = 1.
        for d in order:
            p *= weights[d]/remaining
            remaining -= weights[d]
        return p
    actual_probability = probability(actual)
    result = dict(result_source='User supplied after the original prediction; not independently verified',
        predicted_order=predicted, actual_order=actual,
        podium_members_correct=len(set(predicted)&set(actual)),
        exact_positions_correct=sum(a==b for a,b in zip(predicted,actual)),
        winner_correct=predicted[0]==actual[0],
        actual_order_probability=actual_probability,
        actual_order_negative_log_likelihood=-math.log(actual_probability),
        actual_podium_set_probability=sum(probability(o) for o in itertools.permutations(actual)),
        original_prediction_sha256=hashes[str(m.ROOT/'outputs/prediction.json')],
        original_model_sha256=hashes[str(m.ROOT/'outputs/model.json')],
        antonelli_minus_norris_score_contributions=dict(zip(fitted['features'],
            (contributions['ANT']-contributions['NOR']).tolist())),
        model_retrained=False)
    output = m.ROOT/'post_race'; output.mkdir(exist_ok=True)
    (output/'evaluation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    text = ['# Dutch GP: post-race evaluation','',
        'Actual result supplied by the user after the forecast; not independently verified.','',
        '| Place | Predicted | Actual |','|---|---|---|',
        '| 1 | Kimi Antonelli | Lando Norris |',
        '| 2 | George Russell | Kimi Antonelli |',
        '| 3 | Lando Norris | George Russell |','',
        '**Podium membership: 3/3. Exact positions: 0/3. Winner: incorrect.**','',
        f'Original model probability of the actual ordered podium: {actual_probability:.2%}.',
        f'Probability of these three drivers occupying the podium in any order: {result["actual_podium_set_probability"]:.2%}.','',
        '## What drove the error?','',
        'Norris qualified first, but historical podium rate and team form pushed Antonelli above him.',
        'The table decomposes Antonelli minus Norris in the fitted strength score; positive values favor Antonelli.','',
        '| Feature | Score difference |','|---|---:|']
    text += [f'| {f} | {v:+.3f} |' for f,v in result['antonelli_minus_norris_score_contributions'].items()]
    text += ['', '## What we can learn','',
        'The model identified the podium contenders but failed to order them. One race does not establish that qualifying should always receive greater weight. The next experiment should compare recency windows and qualifying-time features with chronological validation across more races.',
        'This result can become training information for a later race. Once used for model selection or training, the Dutch GP is no longer an untouched test race. A revised model getting this result right would not improve the original forecast record.',
        'Only the podium was supplied. A future update of full-field finishing-form features still needs the remaining finishing positions; they must not be invented.',
        'No coefficients, training data, qualifying inputs, or original predictions were changed. This script evaluates the frozen forecast only.','']
    (output/'EVALUATION.md').write_text('\n'.join(text),encoding='utf-8')
    assert hashes == {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
