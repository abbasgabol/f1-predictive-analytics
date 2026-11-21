# Data card

## Scope

This repository contains local data snapshots for reproducing ten 2026 Grand Prix forecasts, from the Dutch Grand Prix through Las Vegas. Its event store holds qualifying inputs for rounds 1–21 and historical race results for rounds 1–20. Each round has 22 entrants. The latest forecast therefore uses 20 earlier races, or 440 driver entries.

These are project snapshots, not a complete independently verified archive of the season. Event names and ordering are preserved from the supplied and collected data. In particular, the historical source labels include Spain at Madrid and a Bahrain Grand Prix entry in Malaysia at Sepang; retaining those labels is not an independent certification of an official calendar.

## Origin and provenance

Early historical data originated in the user-provided `f1_2026_final_dataset.xlsx`. Later snapshots extend that history with qualifying and race classifications recorded in the original forecast provenance, including references to Formula 1 results pages. The workbook's labels were not independently verified in full.

Each `forecasts/<race-name>/provenance.json` retains source references, cutoff notes, and processing disclosures. Some refer to the original project layout or workbook rather than current paths. Those references document historical origin; they are not dependencies of the current offline loader.

Source classifications were retrieved retrospectively. They may include corrections made after the intended qualifying cutoff, and there is no independently timestamped archive certifying their exact publication state at that cutoff. Recorded hashes support reproducibility of the saved files; they do not resolve that timing limitation.

The [Italian provenance](../forecasts/italy/provenance.json) discloses that a qualifying search incidentally exposed a race-result snippet to the assistant. It was excluded from the model data and the existing model rules were retained, but that forecast is not claimed to be a fully blind assistant forecast.

## Storage and access boundaries

```text
data/events/<round>/qualifying.json    Entrants and qualifying inputs
data/events/<round>/results.json       Historical finishing classifications
data/catalog.json                     Forecast configuration and semantic hashes
data/manifest.json                    File checksums
forecasts/<race-name>/                 Original outputs and provenance
```

There is no round-21 race result in this dataset. Results for earlier forecast targets remain in the event store because they become valid historical inputs for later forecasts. For any particular target, `load_race` opens result files only for strictly earlier rounds. It opens only the qualifying file for the target round.

Qualifying records use these allowed fields: `round`, `gp`, `driver`, `name`, `team`, `qualifying_position`, `q1`, `q2`, and `q3`. Historical results supply driver identifiers and `finish_position`, joined to qualifying by driver. Unknown target fields, mismatched drivers, invalid ranks, missing rounds, and incomplete entrant lists fail validation.

Only qualifying position and earlier results feed the numerical features. Session times, names, and event labels are retained for traceability and presentation; names also identify history groups. The model does not consume target race finishes, race telemetry, pit stops, actual race weather, later standings, or a post-qualifying final grid.

## Processing decisions

- All 22 entrants are retained in each snapshot. Missing or unclassified qualifying positions use rank 22 under the original rule. Examples documented in the snapshots include Hadjar in Singapore, Lawson in Mexico, and Bearman in Las Vegas. These are modeling imputations, not claims about their final starting grid.
- For historical classifications with unclassified entrants, trailing finish ranks follow the recorded table order. This supplies a complete ordering for feature calculations and should not be interpreted as detailed performance measurement among those entrants.
- Driver form uses the last three earlier starts. Team form uses entrants from the team's last three earlier race rounds. Cold-start form defaults to `0.5`; the smoothed prior podium rate starts at `3/22`.
- The shared event store removes repeated copies of identical historical rows. Semantic hashes verify that the reconstructed training history and qualifying target match each forecast's recorded inputs.

## Reproducibility and preservation

Original prediction, fitted-model, report, provenance, and available forecast-freeze files remain under their race-named forecast folders. The manifest records checksums for these artifacts and the event data. `python -m f1predictor verify` checks those files; `verify --replay` also recomputes model outputs and historical evaluation.

The CLI prevents generated output from overwriting `data/` or `forecasts/`. These safeguards protect ordinary use; they do not make files tamper-proof or establish independently certified forecast timestamps. Original embedded paths and implementation hashes refer to the implementation that produced those artifacts, rather than the current shared package.

The earlier investigations in [audits](audits) are retained as historical reports. Their statements and paths should be read in the context of the investigated version. Updating an input snapshot requires an explicit new version; a regenerated prediction from changed data should not be presented as the original forecast.

## Limitations and appropriate interpretation

The 440 driver entries are grouped into only 20 races, with substantial dependence among entrants and across time. This is a small dataset for estimating changing driver and team performance. A correct podium set on one race cannot determine whether a model has learned robust relationships or benefited from chance.

The inputs omit circuit-specific pace, practice long runs, tire strategy, reliability, penalties after qualifying, and race-day conditions. The fixed 22-driver feature scales and complete-history requirements are specific to these snapshots. Supporting different field sizes or new data sources requires deliberate code and schema changes.

Model probabilities are uncalibrated. The chronological backtests are retrospective development checks, not evidence of guaranteed future performance. The project supports reproducible experimentation and examination of its leakage boundaries; it does not claim that perfect source timing or fully blind development has been established.
