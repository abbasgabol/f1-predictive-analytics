# 2026 Singapore Grand Prix prediction

**Marina Bay — cutoff: end of qualifying, 10 October 2026.**

| Predicted position | Driver |
|---|---|
| 1 | Max Verstappen |
| 2 | Kimi Antonelli |
| 3 | Lewis Hamilton |

Selected model: `form_l2_0.03`. Fitted using 16 prior races (352 driver entries).
Model probability of this exact ordered podium: 2.01%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Max Verstappen | 1 | 27.1% | 68.7% |
| Kimi Antonelli | 4 | 26.4% | 67.7% |
| Lewis Hamilton | 3 | 9.5% | 32.4% |
| Charles Leclerc | 2 | 9.3% | 31.8% |
| George Russell | 6 | 8.6% | 29.4% |
| Lando Norris | 5 | 6.1% | 21.6% |
| Oscar Piastri | 7 | 3.0% | 11.0% |
| Pierre Gasly | 8 | 1.8% | 6.8% |
| Liam Lawson | 9 | 1.6% | 6.1% |
| Arvid Lindblad | 10 | 1.4% | 5.1% |
| Nico Hulkenberg | 11 | 1.0% | 3.8% |
| Oliver Bearman | 12 | 0.8% | 3.2% |
| Esteban Ocon | 13 | 0.7% | 2.7% |
| Carlos Sainz | 14 | 0.5% | 1.9% |
| Gabriel Bortoleto | 15 | 0.5% | 1.8% |
| Franco Colapinto | 16 | 0.4% | 1.5% |
| Fernando Alonso | 17 | 0.3% | 1.1% |
| Isack Hadjar | 22 | 0.2% | 0.9% |
| Alexander Albon | 18 | 0.2% | 0.9% |
| Lance Stroll | 19 | 0.2% | 0.7% |
| Sergio Perez | 20 | 0.2% | 0.6% |
| Valtteri Bottas | 21 | 0.1% | 0.5% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Bahrain results are now historical; Singapore race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

Ten chronological tests (rounds 7–16): average 1.80/3 podium drivers, 6/10 winners, 0/10 exact ordered podiums; mean ordered-podium NLL 5.448.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Singapore result has not been loaded or evaluated.
With only 16 races, better future performance is not established. Do not change the rule after seeing the Singapore outcome and then call it an improved Singapore forecast.

## Sources and limitations

- Official Singapore qualifying page: https://www.formula1.com/en/results/2026/races/1296/singapore/qualifying
- All 22 entrants are retained. Hadjar is listed RT without a qualifying time and receives imputed rank 22 under the existing preprocessing rule. This is not a final starting-grid position.
- The only network requests in the data builder are Singapore qualifying and the preceding Bahrain race result. URLs and hashes are in data/provenance.json.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–15 originate in the existing local snapshots; round 16 is the official Bahrain classification. NC entries use official table order for trailing finish ranks.
- No Singapore race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Marina Bay-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
