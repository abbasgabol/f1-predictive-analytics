# 2026 Mexico Grand Prix prediction

**Autodromo Hermanos Rodriguez — cutoff: end of qualifying, 2026 qualifying session.**

| Predicted position | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | Max Verstappen |
| 3 | Lewis Hamilton |

Selected model: `form_l2_0.03`. Fitted using 18 prior races (396 driver entries).
Model probability of this exact ordered podium: 1.44%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Kimi Antonelli | 5 | 23.0% | 60.5% |
| Max Verstappen | 4 | 18.0% | 51.4% |
| Lewis Hamilton | 1 | 15.8% | 46.7% |
| George Russell | 2 | 13.4% | 41.1% |
| Charles Leclerc | 3 | 11.4% | 36.1% |
| Lando Norris | 6 | 5.7% | 19.3% |
| Isack Hadjar | 7 | 3.3% | 11.6% |
| Arvid Lindblad | 8 | 1.8% | 6.3% |
| Oscar Piastri | 12 | 1.4% | 5.1% |
| Pierre Gasly | 9 | 1.4% | 4.9% |
| Nico Hulkenberg | 10 | 1.1% | 4.1% |
| Franco Colapinto | 11 | 0.8% | 2.7% |
| Gabriel Bortoleto | 13 | 0.6% | 2.0% |
| Oliver Bearman | 14 | 0.5% | 1.7% |
| Carlos Sainz | 15 | 0.4% | 1.3% |
| Ryo Hirakawa | 18 | 0.3% | 1.2% |
| Fernando Alonso | 17 | 0.3% | 1.1% |
| Alexander Albon | 16 | 0.3% | 1.0% |
| Lance Stroll | 19 | 0.2% | 0.7% |
| Liam Lawson | 22 | 0.2% | 0.6% |
| Sergio Perez | 20 | 0.1% | 0.5% |
| Valtteri Bottas | 21 | 0.1% | 0.4% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Earlier race results are now historical; Mexico race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

12 chronological tests (rounds 7–18): average 1.92/3 podium drivers, 8/12 winners, 0/12 exact ordered podiums; mean ordered-podium NLL 5.223.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Mexico result has not been loaded or evaluated.
With only 18 races, better future performance is not established. Do not change the rule after seeing the Mexico outcome and then call it an improved Mexico forecast.

## Sources and limitations

- Official Mexico qualifying page: https://www.formula1.com/en/results/2026/races/1298/mexico/qualifying
- All 22 entrants are retained. Unclassified/missing qualifiers use rank 22 under the existing rule; see data/provenance.json for any imputed entrants. This is not the final starting grid.
- The data builder permits this event qualifying, an earlier session only if needed to confirm missing entrants, and the preceding race result. It requires the preceding forecast to be frozen first. URLs and hashes are recorded.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–17 originate in prior snapshots; round 18 is the preceding official race classification. NC entries use table order for trailing ranks.
- No Mexico race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Autodromo Hermanos Rodriguez-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
