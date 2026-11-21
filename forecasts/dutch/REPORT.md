# 2026 Dutch Grand Prix prediction

**Cutoff: end of qualifying, 22 August 2026. Dutch race outcomes are excluded.**

| Predicted place | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | George Russell |
| 3 | Lando Norris |

Model-implied probability of this exact ordered podium: 1.3%.
Probabilities are not independently calibrated. This is a small-data forecast, not a guarantee.

## Driver estimates

| Driver | Qualifying | Win | Second | Third | Any podium |
|---|---:|---:|---:|---:|---:|
| Kimi Antonelli | 3 | 23.6% | 20.1% | 16.6% | 60.3% |
| George Russell | 2 | 16.6% | 15.9% | 14.9% | 47.4% |
| Lando Norris | 1 | 14.9% | 14.7% | 14.1% | 43.7% |
| Lewis Hamilton | 5 | 9.1% | 9.6% | 10.2% | 28.9% |
| Oscar Piastri | 4 | 7.7% | 8.3% | 9.0% | 25.0% |
| Max Verstappen | 7 | 7.1% | 7.7% | 8.4% | 23.3% |
| Charles Leclerc | 6 | 6.7% | 7.3% | 8.0% | 22.1% |
| Liam Lawson | 8 | 3.5% | 3.9% | 4.4% | 11.8% |
| Gabriel Bortoleto | 9 | 2.1% | 2.4% | 2.7% | 7.2% |
| Arvid Lindblad | 10 | 1.8% | 2.1% | 2.4% | 6.3% |
| Yuki Tsunoda | 12 | 1.5% | 1.7% | 2.0% | 5.2% |
| Pierre Gasly | 11 | 1.5% | 1.7% | 1.9% | 5.0% |
| Nico Hulkenberg | 13 | 1.0% | 1.1% | 1.3% | 3.5% |
| Franco Colapinto | 14 | 0.7% | 0.9% | 1.0% | 2.6% |
| Esteban Ocon | 15 | 0.5% | 0.6% | 0.7% | 1.9% |
| Alexander Albon | 16 | 0.4% | 0.5% | 0.6% | 1.5% |
| Carlos Sainz | 17 | 0.3% | 0.4% | 0.5% | 1.2% |
| Fernando Alonso | 18 | 0.3% | 0.3% | 0.4% | 1.0% |
| Lance Stroll | 19 | 0.2% | 0.3% | 0.3% | 0.8% |
| Oliver Bearman | 20 | 0.2% | 0.2% | 0.3% | 0.7% |
| Valtteri Bottas | 21 | 0.1% | 0.2% | 0.2% | 0.5% |
| Sergio Perez | 22 | 0.1% | 0.1% | 0.2% | 0.4% |

## Walk-forward validation

Each of rounds 7–11 is predicted using only earlier races. All drivers from a race stay together.
Hyperparameters and the evaluation window are fixed, not chosen by validation performance.

| Model | Podium drivers correct (of 3), average | Winners correct | Exact ordered podiums | Mean podium negative log likelihood |
|---|---:|---:|---:|---:|
| form_and_qualifying | 1.60 | 2/5 | 0/5 | 5.552 |
| qualifying_only | 1.40 | 3/5 | 0/5 | 5.719 |

## Data and limitations

- Trained on 242 driver entries from the 11 races before the Dutch GP. Only 33 podium placements inform the ranking likelihood.
- Qualifying classifications: official Formula 1 qualifying pages, recorded in data/provenance.json.
- Historical finishing positions: existing local f1_2026_final_dataset.xlsx, rounds 1–11. These labels were not all independently verified.
- Features: qualifying rank, driver last-three-race finishing form, smoothed prior podium rate, and team form over its last three races.
- Drivers omitted from historical qualifying tables receive tied rank 22; historical field membership comes from the local dataset. A new driver uses neutral form and a field-average prior.
- No current-race finishing position, points, status, pit stops, fastest laps, actual race weather, final grid, or current/end-season standings enter the feature matrix.
- Previous race results are valid historical predictors. Current race results are used only as labels for training and historical validation.
- Qualifying tables retrieved retrospectively can include later classification corrections. No archived as-of timestamps are available, so the exact historical publication state is not certified.
- No Dutch race-result endpoint was requested. The model does not read any Dutch race label.
- No track-history, practice pace, sprint, weather forecast, or penalty features are included. Eleven races and five evaluation races are too few to establish robust generalization or calibration.
- The exported coefficients plus feature definitions reproduce the prediction. No target-result scoring is performed.
