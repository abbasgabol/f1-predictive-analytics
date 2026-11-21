# 2026 Las Vegas Grand Prix prediction

**Las Vegas Strip Circuit — cutoff: end of qualifying on 20 November 2026 local time (21 November in Pakistan).**

| Predicted position | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | Max Verstappen |
| 3 | George Russell |

Selected model: `form_l2_0.03`. Fitted using 20 prior races (440 driver entries).
Model probability of this exact ordered podium: 3.90%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Kimi Antonelli | 1 | 37.4% | 81.8% |
| Max Verstappen | 2 | 23.4% | 67.1% |
| George Russell | 3 | 10.9% | 39.5% |
| Lando Norris | 4 | 7.8% | 29.5% |
| Isack Hadjar | 5 | 4.9% | 19.0% |
| Oscar Piastri | 7 | 2.8% | 11.4% |
| Charles Leclerc | 11 | 2.3% | 9.4% |
| Lewis Hamilton | 12 | 2.1% | 8.7% |
| Arvid Lindblad | 6 | 2.0% | 7.9% |
| Liam Lawson | 8 | 1.7% | 7.0% |
| Pierre Gasly | 9 | 1.1% | 4.5% |
| Franco Colapinto | 10 | 0.8% | 3.2% |
| Nico Hulkenberg | 13 | 0.6% | 2.6% |
| Gabriel Bortoleto | 15 | 0.4% | 1.8% |
| Carlos Sainz | 14 | 0.4% | 1.7% |
| Alexander Albon | 16 | 0.3% | 1.3% |
| Rafael Camara | 17 | 0.2% | 1.0% |
| Sergio Perez | 18 | 0.2% | 0.7% |
| Fernando Alonso | 19 | 0.2% | 0.7% |
| Lance Stroll | 20 | 0.1% | 0.5% |
| Valtteri Bottas | 21 | 0.1% | 0.4% |
| Oliver Bearman | 22 | 0.1% | 0.4% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Earlier race results are now historical; Las Vegas race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

14 chronological tests (rounds 7–20): average 1.93/3 podium drivers, 8/14 winners, 0/14 exact ordered podiums; mean ordered-podium NLL 5.420.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Las Vegas result has not been loaded or evaluated.
With only 20 races, better future performance is not established. Do not change the rule after seeing the Las Vegas outcome and then call it an improved Las Vegas forecast.

## Sources and limitations

- Official Las Vegas qualifying page: https://www.formula1.com/en/results/2026/races/1300/las-vegas/qualifying
- All 22 entrants are retained. Unclassified/missing qualifiers use rank 22 under the existing rule; see data/provenance.json for any imputed entrants. This is not the final starting grid.
- The data builder permits this event qualifying, an earlier session only if needed to confirm missing entrants, and the preceding race result. It requires the preceding forecast to be frozen first. URLs and hashes are recorded.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–19 originate in prior snapshots; round 20 is the preceding official Brazilian race classification. NC entries use table order for trailing ranks.
- No Las Vegas race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Las Vegas Strip Circuit-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
