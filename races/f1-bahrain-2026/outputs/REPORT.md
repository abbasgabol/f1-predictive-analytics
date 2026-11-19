# 2026 Bahrain Grand Prix in Malaysia prediction

**Sepang — cutoff: end of qualifying, 3 October 2026.**

| Predicted position | Driver |
|---|---|
| 1 | Kimi Antonelli |
| 2 | Max Verstappen |
| 3 | Lewis Hamilton |

Selected model: `form_l2_0.03`. Fitted using 15 prior races (330 driver entries).
Model probability of this exact ordered podium: 1.97%. Probabilities are uncalibrated.

## Driver estimates

| Driver | Qualifying rank | Win probability | Any podium |
|---|---:|---:|---:|
| Kimi Antonelli | 4 | 28.9% | 70.3% |
| Max Verstappen | 1 | 24.1% | 63.9% |
| Lewis Hamilton | 2 | 9.5% | 31.9% |
| George Russell | 8 | 7.7% | 26.4% |
| Isack Hadjar | 3 | 7.3% | 25.2% |
| Lando Norris | 6 | 5.8% | 20.4% |
| Charles Leclerc | 5 | 5.0% | 17.7% |
| Oscar Piastri | 7 | 3.3% | 12.1% |
| Pierre Gasly | 9 | 1.8% | 6.7% |
| Gabriel Bortoleto | 10 | 1.3% | 4.9% |
| Liam Lawson | 11 | 1.2% | 4.5% |
| Carlos Sainz | 13 | 0.7% | 2.5% |
| Fernando Alonso | 12 | 0.7% | 2.4% |
| Franco Colapinto | 15 | 0.6% | 2.1% |
| Arvid Lindblad | 16 | 0.5% | 1.9% |
| Lance Stroll | 14 | 0.5% | 1.7% |
| Nico Hulkenberg | 17 | 0.4% | 1.4% |
| Oliver Bearman | 18 | 0.3% | 1.2% |
| Esteban Ocon | 19 | 0.3% | 1.0% |
| Alexander Albon | 20 | 0.2% | 0.7% |
| Valtteri Bottas | 21 | 0.1% | 0.6% |
| Sergio Perez | 22 | 0.1% | 0.5% |

## Generalization safeguards

- Same predeclared six candidates: qualifying-only or four pre-race features; L2 0.03, 0.1, or 0.3.
- Selection uses expanding-window validation on earlier races only. The one-standard-error heuristic favors simpler models; it does not guarantee absence of overfitting.
- No random driver-row split, target-result tuning, or target race labels.
- Previous race outcomes are valid training labels. Azerbaijan results are now historical; Bahrain race results were not requested or used.
- The selected qualifying-only model, if chosen, ranks drivers by qualifying order. Its learned coefficient controls how uncertain its probabilities are; it does not memorize driver names.

## Retrospective outer validation

Nine chronological tests (rounds 7–15): average 1.67/3 podium drivers, 6/9 winners, 0/9 exact ordered podiums; mean ordered-podium NLL 5.609.
These are retrospective development checks, not new untouched tests. Prior race results were already available during development. The Bahrain result has not been loaded or evaluated.
With only 15 races, better future performance is not established. Do not change the rule after seeing the Bahrain outcome and then call it an improved Bahrain forecast.

## Sources and limitations

- Official Bahrain qualifying page: https://www.formula1.com/en/results/2026/races/1308/bahrain/qualifying
- All 22 target entrants have qualifying classifications. Teams and driver identities are taken from this event, including driver/team changes.
- The only network requests in the data builder are Bahrain qualifying and the preceding Azerbaijan race result. URLs and hashes are in data/provenance.json.
- Retrospectively retrieved qualifying classifications may include corrections after the cutoff; an exact timestamped archive is unavailable.
- Historical rounds 1–14 originate in the existing local snapshots; round 15 is the official Azerbaijan classification. NC entries use official table order for trailing finish ranks.
- No Bahrain race telemetry, result, pit stops, actual weather, final grid, or later standings are included.
- No Sepang-specific historical race form is modeled. The small dataset and omitted pace/weather/penalty information limit accuracy.
