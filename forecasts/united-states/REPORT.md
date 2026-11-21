# 2026 United States Grand Prix prediction

**Circuit of the Americas — cutoff: end of qualifying, 2026 qualifying session.**

| Predicted position | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | Max Verstappen |
| 3 | Charles Leclerc |

Selected model: `form_l2_0.03`. Fitted using 17 prior races (374 driver entries).
Model probability of this exact ordered podium: 2.58%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Kimi Antonelli | 1 | 38.8% | 82.5% |
| Max Verstappen | 2 | 21.6% | 63.9% |
| Charles Leclerc | 4 | 7.4% | 28.1% |
| Lewis Hamilton | 5 | 6.7% | 25.7% |
| George Russell | 6 | 6.6% | 25.1% |
| Isack Hadjar | 3 | 6.4% | 24.5% |
| Lando Norris | 8 | 3.0% | 11.8% |
| Oscar Piastri | 7 | 2.7% | 10.7% |
| Arvid Lindblad | 9 | 1.4% | 5.7% |
| Liam Lawson | 10 | 1.2% | 5.0% |
| Pierre Gasly | 11 | 0.8% | 3.3% |
| Nico Hulkenberg | 12 | 0.7% | 2.9% |
| Gabriel Bortoleto | 13 | 0.5% | 2.1% |
| Franco Colapinto | 14 | 0.4% | 1.7% |
| Oliver Bearman | 16 | 0.4% | 1.5% |
| Fernando Alonso | 15 | 0.3% | 1.4% |
| Esteban Ocon | 17 | 0.3% | 1.2% |
| Lance Stroll | 18 | 0.2% | 0.8% |
| Carlos Sainz | 19 | 0.2% | 0.7% |
| Alexander Albon | 20 | 0.1% | 0.5% |
| Sergio Perez | 21 | 0.1% | 0.5% |
| Valtteri Bottas | 22 | 0.1% | 0.4% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Earlier race results are now historical; United States race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

11 chronological tests (rounds 7–17): average 1.82/3 podium drivers, 7/11 winners, 0/11 exact ordered podiums; mean ordered-podium NLL 5.338.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The United States result has not been loaded or evaluated.
With only 17 races, better future performance is not established. Do not change the rule after seeing the United States outcome and then call it an improved United States forecast.

## Sources and limitations

- Official United States qualifying page: https://www.formula1.com/en/results/2026/races/1297/united-states/qualifying
- All 22 entrants are retained. Unclassified/missing qualifiers use rank 22 under the existing rule; see data/provenance.json for any imputed entrants. This is not the final starting grid.
- The data builder permits this event qualifying, an earlier session only if needed to confirm missing entrants, and the preceding race result. It requires the preceding forecast to be frozen first. URLs and hashes are recorded.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–16 originate in prior snapshots; round 17 is the preceding official race classification. NC entries use table order for trailing ranks.
- No United States race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Circuit of the Americas-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
