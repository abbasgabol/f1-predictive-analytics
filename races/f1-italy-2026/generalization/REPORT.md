# Generalization review

The aim is reliable unseen-race predictions, not test scores exceeding training scores.

## Fixed evaluation protocol

- Six outer tests: rounds 7–12. Each is fitted using earlier whole races only.
- Inner tests: train through round 3, predict round 4, then expand up to the race before the outer test.
- Six candidates only: qualifying alone or the existing four features, each with L2 0.03, 0.1, or 0.3.
- Select by ordered-podium negative log likelihood (NLL); lower is better. Within one standard error of the best inner score, prefer fewer features and then stronger regularization.
- Outer test outcomes never select the model for that fold. Features use strictly previous race outcomes.
- No new features, driver identity memorization, random row splits, target-result tuning, or new race-result retrieval.

## Retrospective held-out scores

| Method | Mean NLL (lower better) | Podium members / 3 | Winners | Exact ordered podiums |
|---|---:|---:|---:|---:|
| nested_selection | 5.566 | 1.67 | 4/6 | 0/6 |
| original | 5.377 | 1.83 | 2/6 | 0/6 |
| qualifying_baseline | 5.566 | 1.67 | 4/6 | 0/6 |

Nested model mean training NLL: 5.649; mean outer-test NLL: 5.566.
These means concern different races and sample sizes; the gap alone cannot prove or disprove overfitting.

## Selected models by held-out race

| Test round | Selected candidate | Training NLL | Test NLL |
|---|---|---:|---:|
| 7 | qualifying_l2_0.03 | 5.675 | 5.005 |
| 8 | qualifying_l2_0.03 | 5.540 | 5.731 |
| 9 | qualifying_l2_0.03 | 5.574 | 6.511 |
| 10 | qualifying_l2_0.03 | 5.723 | 5.329 |
| 11 | qualifying_l2_0.03 | 5.668 | 6.022 |
| 12 | qualifying_l2_0.03 | 5.712 | 4.801 |

## Limits and next test

These historical results have already been seen during development. Nested validation prevents within-fold leakage, but does not erase analyst exposure or create a new untouched test set.
Twelve races means only 36 observed podium placements. Six outer races are too few to establish a reliable advantage. The one-standard-error rule is a simplicity heuristic; overlapping chronological folds are dependent.
Stronger regularization can underfit. Do not adopt a new method solely because it wins one metric on this small retrospective comparison.
The fixed inner-selection rule proposes `qualifying_l2_0.03` after all 12 historical races. Its coefficients are saved separately for prospective evaluation; the original forecasts are preserved.
Before evaluating another race, freeze the data cutoff and selection rule. Record the forecast before viewing its outcome, then score every race without selectively skipping failures. Collect more time-ordered seasons for stronger validation, while accounting for regulation changes.
The Italian race outcome supplied in chat is not ingested here. No future performance improvement or absence of overfitting is guaranteed.
