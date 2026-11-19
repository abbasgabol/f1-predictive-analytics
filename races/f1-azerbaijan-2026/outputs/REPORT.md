# 2026 Azerbaijan Grand Prix prediction

**Baku — cutoff: end of qualifying, 25 September 2026.**

| Predicted position | Driver |
|---|---|
| 1 | George Russell |
| 2 | Charles Leclerc |
| 3 | Lando Norris |

Selected model: `form_l2_0.03`. Fitted using 14 prior races (308 driver entries).
Model probability of this exact ordered podium: 0.92%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| George Russell | 1 | 30.9% | 70.7% |
| Charles Leclerc | 2 | 11.1% | 35.1% |
| Lando Norris | 5 | 10.7% | 34.1% |
| Oscar Piastri | 3 | 10.3% | 32.8% |
| Max Verstappen | 8 | 6.8% | 22.9% |
| Lewis Hamilton | 6 | 6.2% | 20.9% |
| Isack Hadjar | 4 | 5.6% | 19.1% |
| Kimi Antonelli | 16 | 4.7% | 16.1% |
| Pierre Gasly | 7 | 3.6% | 12.5% |
| Franco Colapinto | 10 | 1.8% | 6.5% |
| Carlos Sainz | 9 | 1.7% | 6.1% |
| Liam Lawson | 12 | 1.2% | 4.4% |
| Oliver Bearman | 11 | 1.2% | 4.2% |
| Alexander Albon | 13 | 0.8% | 3.0% |
| Arvid Lindblad | 15 | 0.7% | 2.6% |
| Esteban Ocon | 14 | 0.7% | 2.5% |
| Gabriel Bortoleto | 17 | 0.5% | 1.8% |
| Nico Hulkenberg | 18 | 0.4% | 1.5% |
| Fernando Alonso | 19 | 0.3% | 1.0% |
| Sergio Perez | 20 | 0.2% | 0.8% |
| Lance Stroll | 21 | 0.2% | 0.7% |
| Valtteri Bottas | 22 | 0.2% | 0.6% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Spanish results are now historical; Azerbaijan race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

Eight chronological tests (rounds 7–14): average 1.75/3 podium drivers, 5/8 winners, 0/8 exact ordered podiums; mean ordered-podium NLL 5.574.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Azerbaijan result has not been loaded or evaluated.
With only 14 races, better future performance is not established. Do not change the rule after seeing the Azerbaijan outcome and then call it an improved Azerbaijan forecast.

## Sources and limitations

- Official Azerbaijan qualifying page: https://www.formula1.com/en/results/2026/races/1295/azerbaijan/qualifying
- All 22 target entrants have qualifying classifications. Teams and driver identities are taken from this event, including driver/team changes.
- The only network requests in the data builder are Azerbaijan qualifying and the preceding Spanish race result. URLs and hashes are in data/provenance.json.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–13 originate in the existing local snapshots; round 14 is the official Spanish classification. NC entries use official table order for trailing finish ranks.
- No Azerbaijan race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Baku-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
