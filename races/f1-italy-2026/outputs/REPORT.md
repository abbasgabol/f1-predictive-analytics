# 2026 Italian Grand Prix prediction

**Cutoff: end of qualifying, 5 September 2026. Italian race outcomes are excluded.**

| Predicted place | Driver |
|---|---|
| 1 | George Russell |
| 2 | Kimi Antonelli |
| 3 | Charles Leclerc |

Model-implied probability of this exact ordered podium: 0.6%.
Probabilities are not independently calibrated. This is a small-data forecast, not a guarantee.

## Driver estimates

| Driver | Qualifying | Win | Second | Third | Any podium |
|---|---:|---:|---:|---:|---:|
| George Russell | 2 | 20.1% | 17.7% | 15.3% | 53.1% |
| Kimi Antonelli | 7 | 13.7% | 13.4% | 12.8% | 40.0% |
| Charles Leclerc | 4 | 10.9% | 11.0% | 11.1% | 33.0% |
| Pierre Gasly | 1 | 10.8% | 11.0% | 11.0% | 32.8% |
| Oscar Piastri | 3 | 10.5% | 10.6% | 10.7% | 31.8% |
| Lewis Hamilton | 5 | 10.1% | 10.3% | 10.5% | 30.8% |
| Max Verstappen | 6 | 8.0% | 8.3% | 8.7% | 25.0% |
| Lando Norris | 9 | 4.2% | 4.6% | 5.0% | 13.9% |
| Franco Colapinto | 8 | 2.6% | 2.9% | 3.2% | 8.6% |
| Arvid Lindblad | 10 | 1.9% | 2.1% | 2.4% | 6.4% |
| Gabriel Bortoleto | 11 | 1.6% | 1.8% | 2.0% | 5.3% |
| Nico Hulkenberg | 13 | 1.1% | 1.2% | 1.4% | 3.7% |
| Liam Lawson | 14 | 1.0% | 1.1% | 1.3% | 3.4% |
| Oliver Bearman | 12 | 0.9% | 1.1% | 1.2% | 3.2% |
| Yuki Tsunoda | 17 | 0.6% | 0.6% | 0.7% | 1.9% |
| Carlos Sainz | 15 | 0.6% | 0.6% | 0.7% | 1.9% |
| Esteban Ocon | 16 | 0.4% | 0.5% | 0.6% | 1.5% |
| Alexander Albon | 18 | 0.3% | 0.4% | 0.4% | 1.1% |
| Valtteri Bottas | 19 | 0.2% | 0.3% | 0.3% | 0.8% |
| Sergio Perez | 20 | 0.2% | 0.2% | 0.3% | 0.7% |
| Fernando Alonso | 21 | 0.2% | 0.2% | 0.2% | 0.6% |
| Lance Stroll | 22 | 0.2% | 0.2% | 0.2% | 0.5% |

## Walk-forward validation

Each of rounds 7–12 is predicted using only earlier races. All drivers from a race stay together.
Hyperparameters and the evaluation window are fixed, not chosen by validation performance.

| Model | Podium drivers correct (of 3), average | Winners correct | Exact ordered podiums | Mean podium negative log likelihood |
|---|---:|---:|---:|---:|
| form_and_qualifying | 1.83 | 2/6 | 0/6 | 5.377 |
| qualifying_only | 1.67 | 4/6 | 0/6 | 5.566 |

## Data and limitations

- Trained on 264 driver entries from the 12 races before the Italian GP. Only 36 podium placements inform the ranking likelihood.
- Qualifying classifications: official Formula 1 qualifying pages, recorded in data/provenance.json.
- Historical finishing positions: existing local f1_2026_final_dataset.xlsx, rounds 1–12. These labels were not all independently verified.
- Features: qualifying rank, driver last-three-race finishing form, smoothed prior podium rate, and team form over its last three races.
- Drivers omitted from historical qualifying tables receive tied rank 22; historical field membership comes from the local dataset. A new driver uses neutral form and a field-average prior.
- No current-race finishing position, points, status, pit stops, fastest laps, actual race weather, final grid, or current/end-season standings enter the feature matrix.
- Previous race results are valid historical predictors. Current race results are used only as labels for training and historical validation.
- Qualifying tables retrieved retrospectively can include later classification corrections. No archived as-of timestamps are available, so the exact historical publication state is not certified.
- An initial qualifying search incidentally exposed a race-result snippet to the assistant. The unchanged model and its data do not use it; this is not claimed to be a fully blind assistant forecast.
- No track-history, practice pace, sprint, weather forecast, or penalty features are included. Twelve races and six evaluation races are too few to establish robust generalization or calibration.
- The exported coefficients plus feature definitions reproduce the prediction. No target-result scoring is performed.
