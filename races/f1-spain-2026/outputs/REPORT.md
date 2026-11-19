# 2026 Spanish Grand Prix prediction

**Madrid — cutoff: end of qualifying, 12 September 2026.**

| Predicted position | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | Lando Norris |
| 3 | Max Verstappen |

Selected model: `form_l2_0.03`. Fitted using 13 prior races (286 driver entries).
Model probability of this exact ordered podium: 1.92%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Kimi Antonelli | 2 | 37.6% | 79.9% |
| Lando Norris | 1 | 13.7% | 44.9% |
| Max Verstappen | 3 | 11.3% | 38.3% |
| George Russell | 6 | 9.6% | 33.4% |
| Lewis Hamilton | 4 | 7.6% | 27.2% |
| Charles Leclerc | 5 | 5.6% | 20.6% |
| Oscar Piastri | 7 | 3.7% | 13.8% |
| Liam Lawson | 8 | 2.1% | 8.0% |
| Franco Colapinto | 9 | 1.6% | 6.2% |
| Arvid Lindblad | 10 | 1.4% | 5.5% |
| Nico Hulkenberg | 11 | 1.2% | 4.4% |
| Gabriel Bortoleto | 12 | 1.0% | 3.7% |
| Pierre Gasly | 14 | 0.8% | 2.9% |
| Yuki Tsunoda | 15 | 0.6% | 2.5% |
| Esteban Ocon | 13 | 0.6% | 2.4% |
| Alexander Albon | 16 | 0.4% | 1.5% |
| Carlos Sainz | 17 | 0.3% | 1.2% |
| Fernando Alonso | 18 | 0.3% | 1.0% |
| Sergio Perez | 19 | 0.2% | 0.8% |
| Valtteri Bottas | 20 | 0.2% | 0.7% |
| Lance Stroll | 22 | 0.1% | 0.5% |
| Oliver Bearman | 22 | 0.1% | 0.5% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Italian results are now historical; Spanish race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

Seven chronological tests (rounds 7–13): average 1.57/3 podium drivers, 4/7 winners, 0/7 exact ordered podiums; mean ordered-podium NLL 5.799.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Spanish result has not been loaded or evaluated.
With only 13 races, better future performance is not established. Do not change the rule after seeing the Spanish outcome and then call it an improved Spanish forecast.

## Sources and limitations

- Official Spanish qualifying page: https://www.formula1.com/en/results/2026/races/1294/spain/qualifying
- Bearman and Stroll are absent from the published qualifying table but present in practice 3. Both receive tied qualifying rank 22, following the existing preprocessing rule; this is an imputation, not their final starting grid.
- The only network requests in the data builder are Spanish qualifying, Spanish practice 3, and the preceding Italian race result. URLs and hashes are in data/provenance.json.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–12 originate in the existing local snapshots; round 13 is the official Italian classification. Italian NC entries use official table order for trailing finish ranks.
- No Spanish race telemetry, result, pit stops, actual weather, final grid, or later standings are included. Practice is used only to confirm missing qualifying entrants.
- No Madrid-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
