# 2026 Brazil Grand Prix prediction

**Interlagos — cutoff: end of qualifying, 2026 qualifying session.**

| Predicted position | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | George Russell |
| 3 | Lando Norris |

Selected model: `form_l2_0.03`. Fitted using 19 prior races (418 driver entries).
Model probability of this exact ordered podium: 3.02%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Kimi Antonelli | 3 | 38.4% | 81.4% |
| George Russell | 2 | 15.7% | 50.8% |
| Lando Norris | 1 | 14.2% | 47.1% |
| Charles Leclerc | 4 | 10.0% | 35.4% |
| Liam Lawson | 5 | 3.3% | 12.6% |
| Isack Hadjar | 7 | 3.2% | 12.4% |
| Lewis Hamilton | 11 | 3.1% | 12.1% |
| Max Verstappen | 16 | 2.4% | 9.5% |
| Nico Hulkenberg | 6 | 2.4% | 9.3% |
| Oscar Piastri | 12 | 1.4% | 5.4% |
| Oliver Bearman | 8 | 1.3% | 5.1% |
| Alexander Albon | 10 | 1.0% | 3.8% |
| Fernando Alonso | 9 | 0.9% | 3.7% |
| Rafael Camara | 13 | 0.8% | 3.2% |
| Arvid Lindblad | 14 | 0.6% | 2.2% |
| Carlos Sainz | 15 | 0.4% | 1.6% |
| Pierre Gasly | 18 | 0.3% | 1.1% |
| Franco Colapinto | 17 | 0.2% | 1.0% |
| Lance Stroll | 19 | 0.2% | 0.6% |
| Gabriel Bortoleto | 22 | 0.1% | 0.5% |
| Valtteri Bottas | 20 | 0.1% | 0.5% |
| Sergio Perez | 21 | 0.1% | 0.5% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Earlier race results are now historical; Brazil race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

13 chronological tests (rounds 7–19): average 2.00/3 podium drivers, 8/13 winners, 0/13 exact ordered podiums; mean ordered-podium NLL 5.162.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Brazil result has not been loaded or evaluated.
With only 19 races, better future performance is not established. Do not change the rule after seeing the Brazil outcome and then call it an improved Brazil forecast.

## Sources and limitations

- Official Brazil qualifying page: https://www.formula1.com/en/results/2026/races/1299/brazil/qualifying
- All 22 entrants are retained. Unclassified/missing qualifiers use rank 22 under the existing rule; see data/provenance.json for any imputed entrants. This is not the final starting grid.
- The data builder permits this event qualifying, an earlier session only if needed to confirm missing entrants, and the preceding race result. It requires the preceding forecast to be frozen first. URLs and hashes are recorded.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–18 originate in prior snapshots; round 19 is the preceding official race classification. NC entries use table order for trailing ranks.
- No Brazil race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Interlagos-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
