# Does the model improve on qualifying?

Run `python scripts/evaluate_baselines.py` to reproduce this comparison from the saved forecasts and event snapshots.

## Ten saved forecasts

| Method | Correct podium names | Winners |
| --- | ---: | ---: |
| Forecast as saved | 22/30 | 4/10 |
| Use qualifying order | 17/30 | 6/10 |

The model changed at least one qualifying top-three name in six races. Across eight replacement picks, six new drivers made the actual podium and one of the dropped qualifiers made it. The five net gains came from four races. This sample includes user-supplied and archived outcomes. The Italian forecast has a [research exposure disclosure](../forecasts/italy/provenance.json).

## Four model variants tested on the same 14 historical rounds

Each round from 7 through 20 is held out as a whole. Each model is trained on strictly earlier rounds. Within each feature family, the same three regularization strengths and chronological selection rule are applied using earlier data. These historical rounds overlap with the ten-forecast evaluation, so the two tables should be read separately.

| Features and policy | Podium names | Winners | Exact podiums | Mean ordered-podium log loss |
| --- | ---: | ---: | ---: | ---: |
| Qualifying alone | 23/42 | 9/14 | 0/14 | 5.865 |
| Earlier driver and team form alone | 23/42 | 4/14 | 0/14 | 6.354 |
| Qualifying and earlier form | 29/42 | 6/14 | 0/14 | 5.222 |
| Current policy chooses qualifying alone or qualifying and form per round | 27/42 | 8/14 | 0/14 | 5.420 |

Lower log loss means the model assigned more probability to the observed ordered podium on average. The current policy chose qualifying alone in seven of the 14 rounds. Adding form helped the model find more podium names and improved log loss in these historical tests, while qualifying alone picked more winners. The chronological split reduces look-ahead, but these small retrospective comparisons do not settle how well the model will generalize.

## How to test a richer model

- Add race-level qualifying and finish records from earlier seasons. Keep complete races together, train on older seasons, and validate on later seasons to measure how well the signals transfer across changes in teams and regulations.
- Join races by circuit and layout. Compute circuit history only from earlier races, including how often drivers gained positions and how frequently pole converted to a win.
- Use a weather forecast issued at or before the prediction cutoff for the race time. Store the issue timestamp and verify coverage before using this feature. Actual race weather is available only after the cutoff for a forecast made at qualifying.
- Compare each feature group against pole position and the top three qualifiers. Report winner accuracy, unordered podium picks, exact order, and log loss separately. Freeze the approach before the next unseen race.
