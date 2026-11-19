# Dutch GP: post-race evaluation

Actual result supplied by the user after the forecast; not independently verified.

| Place | Predicted | Actual |
|---|---|---|
| 1 | Kimi Antonelli | Lando Norris |
| 2 | George Russell | Kimi Antonelli |
| 3 | Lando Norris | George Russell |

**Podium membership: 3/3. Exact positions: 0/3. Winner: incorrect.**

Original model probability of the actual ordered podium: 1.11%.
Probability of these three drivers occupying the podium in any order: 6.80%.

## What drove the error?

Norris qualified first, but historical podium rate and team form pushed Antonelli above him.
The table decomposes Antonelli minus Norris in the fitted strength score; positive values favor Antonelli.

| Feature | Score difference |
|---|---:|
| qualifying_quality | -0.370 |
| driver_last3_finish_quality | -0.006 |
| driver_prior_podium_rate | +0.777 |
| team_last3_races_finish_quality | +0.059 |

## What we can learn

The model identified the podium contenders but failed to order them. One race does not establish that qualifying should always receive greater weight. The next experiment should compare recency windows and qualifying-time features with chronological validation across more races.
This result can become training information for a later race. Once used for model selection or training, the Dutch GP is no longer an untouched test race. A revised model getting this result right would not improve the original forecast record.
Only the podium was supplied. A future update of full-field finishing-form features still needs the remaining finishing positions; they must not be invented.
No coefficients, training data, qualifying inputs, or original predictions were changed. This script evaluates the frozen forecast only.
