# Bahrain model leakage audit

No evidence of target-result leakage in the saved Bahrain modeling pipeline under these tests.

## Executed checks

- **PASS — Training cutoff and target field allowlist:** 330 rows from rounds 1–15; 22 Bahrain qualifying rows, no target outcome fields.
- **PASS — Frozen input and implementation hashes:** Every recorded data/code SHA-256 matches the original forecast artifact.
- **PASS — Independent feature reconstruction:** All 352 driver rows agree with independently calculated strictly-prior-race features.
- **PASS — Every-race future-label poisoning:** Changing current/future outcomes cannot change the features for any of rounds 1–15.
- **PASS — Target contamination rejected:** Six prohibited field types and Bahrain rows injected into training are rejected by production validation.
- **PASS — Row-order and identity controls:** Training-row shuffling and consistent driver/team anonymization preserve fitted coefficients and target features.
- **PASS — Offline clean-room production replay:** Entire prediction JSON reproduced exactly, including selection, probabilities and validation; original project/workbooks and network access blocked.
- **PASS — Random-label negative control completed:** Real labels: 1.889/3 mean hits; shuffled labels: 0.430/3. See caveats; this is supporting evidence, not proof.

## Interpretation

Correct podium names alone do not establish leakage. The model can reproduce the forecast from only earlier race results and qualifying inputs. It does not need to read Bahrain race labels, saved predictions, or a network service to compute its prediction.
A random-label control disrupts the real relationship between features and outcomes. Losing useful predictive signal under this control is reassuring, but is not an exhaustive proof of no leakage.
The 80% podium-driver hit rate previously quoted came from five sequential chat forecasts, not a large independent benchmark. It does not imply 80% probability of an exact ordered podium.

## What this cannot prove

- Cannot certify upstream workbook labels or the exact historical publication state of qualifying pages.
- Hashes demonstrate consistency with saved artifacts, not independently timestamped provenance.
- Italian forecast had incidental assistant search exposure; code audit cannot make the full conversation blind.
- Repeated model development on known history and a small sample limit claims about generalization.
- No Bahrain actual outcome is used in these tests or model fitting.

## Simple baseline on the five supplied results

Picking the top three qualifiers would have identified 10 of 15 podium drivers. The saved model forecasts identified 12 of 15. Both methods picked all three names for the Dutch and Spanish races. This comparison uses the user-supplied actual results only for evaluation; it is not an independent benchmark. Historical snapshot prefixes were also confirmed unchanged across the five projects.
