# Methodology

## Prediction task and information boundary

For a target Grand Prix, predict an ordered podium and each entrant's probability of winning or reaching the podium. Inputs consist of that race's qualifying classification and qualifying/result snapshots from strictly earlier rounds. The target race's result is never an input to the prediction loader.

The repository reproduces ten saved forecasts. It does not automatically download a new season or infer the current race. Race configuration and snapshot hashes live in `data/catalog.json`.

## Features

The 22-driver snapshots use four numerical features. Let `q` be qualifying position and `p` be historical finishing position.

| Feature | Calculation |
| --- | --- |
| Qualifying quality | `(23 - q) / 22` |
| Driver recent form | Mean `(23 - p) / 22` over the driver's last three earlier starts |
| Driver prior podium rate | `(earlier podiums + 2 × 3/22) / (earlier starts + 2)` |
| Team recent form | Mean `(23 - p) / 22` for the team's entrants across its last three earlier race rounds |

For every row, eligible history satisfies `historical_round < row_round`. This also applies when constructing features for historical training examples. A race's own finish can supply its training label, but cannot enter that race's features.

Drivers or teams without earlier finishing history receive neutral form `0.5`. A new driver's smoothed podium rate starts at `3/22`. Driver and team identifiers join and group history; the model does not learn a coefficient for each driver's name. Qualifying session times are retained in source snapshots but are not fitted features.

## Ranking model

For driver `i`, a linear score `s_i = x_i · w` defines positive strength `a_i = exp(s_i)`. The Plackett–Luce model selects the first driver, removes that driver, selects the second, and then the third. With total strength `A`, an ordered podium `(i, j, k)` has probability:

```text
P(i, j, k) = (a_i / A)
             × (a_j / (A - a_i))
             × (a_k / (A - a_i - a_j))
```

Weights minimize historical top-three negative log-likelihood plus an L2 penalty. SciPy's L-BFGS-B optimizer uses an analytic gradient; log-sum-exp calculations stabilize likelihood evaluation. The complete historical classification supports lagged features, while the likelihood directly models the observed top three.

The predicted podium follows descending model scores. Exact enumeration of all `22 × 21 × 20 = 9,240` distinct ordered podiums yields position and podium marginals. There is no Monte Carlo sampling error in that calculation. These are probabilities under the fitted model, not empirically calibrated confidence levels.

## Model selection

The first two forecasts, Dutch and Italian, preserve the original fixed four-feature model with L2 `0.03`. Subsequent forecasts use the same six-candidate search:

- Qualifying-only or all four features.
- L2 strength `0.03`, `0.1`, or `0.3` for either feature set.

For a target round, selection evaluates candidates on expanding chronological windows. The first inner validation race is round 4, trained on rounds 1–3. Every subsequent inner race is scored by a model trained only on its earlier rounds. Selection averages ordered-podium negative log-likelihood over eligible inner races.

The one-standard-error heuristic admits candidates within one estimated standard error of the best mean loss. Among them it prefers fewer features, then stronger regularization. This constrains flexibility; it does not guarantee that overfitting is absent. Overlapping training windows make the folds dependent, so the standard error should not be treated as a formal independent-sample confidence bound.

## Chronological evaluation

Outer evaluation begins at round 7. For each outer test race:

1. Restrict available training data and model selection to earlier rounds.
2. Choose a candidate with inner chronological validation, or retain the fixed model for a fixed-policy forecast.
3. Fit the chosen model on all earlier rounds.
4. Predict from that test race's qualifying and earlier form.
5. Compare with its historical result after the prediction is produced.

No random split of driver rows is used. Entrants from one race remain together, and future races cannot train a model evaluated on an earlier race.

| Metric | Interpretation |
| --- | --- |
| Mean podium hits | Number of predicted drivers in the actual podium, ignoring order; maximum 3 |
| Winners correct | Count of tests with the correct first-place driver |
| Exact orders | Count of tests with all three positions correct |
| Ordered-podium NLL | Negative log probability assigned to the actual ordered podium; lower is better |

The frozen Las Vegas run has 20 training races and 440 driver entries. Across 14 outer tests, rounds 7–20, it records mean podium hits **1.93/3**, **8/14** winners, **0/14** exact ordered podiums, and mean NLL **5.420**. See the [original report](../forecasts/las-vegas/REPORT.md).

These are retrospective checks performed during development. Earlier outcomes were available to the developer, and model design was not evaluated against a newly sealed external test set. Nested chronological selection protects the implemented selection procedure; it cannot undo earlier human exposure or certify an independent benchmark. A proper future evaluation should freeze the full procedure before collecting new race outcomes and report all consecutive forecasts.

Generalization means useful performance on unseen races. There is no requirement that test performance exceed training performance, and changing a model specifically to achieve that comparison would not establish better generalization.

## Shared implementation and optimization

`Trainer` owns a copy of its historical dataset. It builds each race's lagged feature matrix once, then caches fits and scores by cutoff, candidate, and fitting policy within that dataset instance. Cached coefficients and score records are returned as copies. This avoids repeated work without reusing fits across unrelated datasets or cutoffs.

The probability calculation uses vectorized NumPy indexing over all distinct podium triples. These changes preserve the original model policies; they are implementation optimizations rather than new predictive evidence. `verify --replay` compares regenerated coefficients and probabilities within numerical tolerances, plus predicted podiums and backtest results, against the ten frozen forecasts.

Tests also check temporal feature boundaries, future-label poisoning, identity anonymization, numerical gradients, independent probability enumeration, protected input schemas, and cache behavior. Snapshot checksums establish consistency with recorded files, not independent proof of source timing. See the [data card](data-card.md) for the remaining provenance limitations.
