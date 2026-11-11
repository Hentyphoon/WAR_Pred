# Models

WAR_pred forecasts a hitter's next-season offensive value. This document covers how the models work, what they assume, and why they were built this way.

**Status:** results are from the 2026-11-08 run of `ML/notebook/ML.ipynb`. The app serves these models.

## Summary

| | |
|---|---|
| Question answered | If this hitter gets at least 100 PA next season, what will they produce? |
| Outputs | wRAA, BsR, RLR, and offensive WAR (oWAR) derived from them |
| Inputs | The previous three seasons and the player's age |
| Data | Lahman-style batting, pitching, and people tables through 2024 |
| Seasons used | 1961 onward |
| Selected model | Gradient boosting, one model per target |
| Test result | oWAR R² 0.399, mean absolute error 1.03 WAR (2015–2024, excluding 2020) |

## Pipeline

1. `Migration/cleaner.py` builds player-season and league-season stats from the CSVs.
2. `Migration/main.py` writes them to `playerstat` and `leaguestat`.
3. `ML/notebook/ML.ipynb` computes the metrics, writes `playersabermetric`, trains and evaluates the models, and saves them to `ML/app/model/`.

To reproduce, run `python main.py` from `Migration/`, then run the notebook from top to bottom. The model folder is gitignored, so the notebook has to be run to recreate it.

## Metrics

| Metric | Formula |
|---|---|
| wOBA | (0.69·uBB + 0.72·HBP + 0.88·1B + 1.247·2B + 1.578·3B + 2.031·HR) / (AB + uBB + HBP + SF) |
| wRAA | ((wOBA − league wOBA) / 1.25) × PA |
| Runs per out (RPO) | league R / (league IP × 3) |
| runCS | −(2 × RPO + 0.075) |
| league wSB | (lgSB × 0.2 + lgCS × runCS) / (lg1B + lgBB + lgHBP − lgIBB) |
| wSB | SB × 0.2 + CS × runCS − league wSB × (1B + BB + HBP − IBB) |
| wGDP | ((lgGDP / lgGDP_OPP) × GDP_OPP − GDP) × RPO |
| BsR | wSB + wGDP |
| RPW (runs per win) | 9 × (league R / league IP) × 1.5 + 3 |
| RLR (replacement runs) | 0.235 × league games × RPW × PA / league PA |
| oWAR | (wRAA + BsR + RLR) / RPW |

The formulas follow the FanGraphs definitions, except where the assumptions below say otherwise.

## Assumptions

### Data

| Assumption | Reasoning | Effect |
|---|---|---|
| Blank HBP, SF, SH, IBB, SB, CS, and GDP count as 0 | These stats weren't recorded in early seasons, and a blank must not erase the player's PA | Pre-1961 rates are approximate; little effect from 1961 on, where these fields are complete |
| GDP opportunities = PA − HR − BB − HBP − SF | The data has no real count of double-play situations | Overstates opportunities, so wGDP is a rough estimate |
| League games = IP / 18 | The `G` column sums pitcher appearances, not games | Lets replacement level scale with short seasons and fewer teams |
| Age = season − birth year | Only the year is used | Can be off by up to one year against the usual July 1 convention |
| Multi-team seasons are summed | One row per player-season is simpler to model | Team context is lost |

### Baseball

| Assumption | Reasoning | Effect |
|---|---|---|
| Fixed wOBA weights and a 1.25 scale for every season | Season-specific weights aren't available in this data | Era differences are only partly captured |
| League wOBA includes pitchers batting | It's computed from all batting lines | The baseline is lower before the universal DH |
| No fielding, positional, park, or league adjustment | Earlier work found no usable positional data | oWAR will differ from published WAR |
| BsR excludes UBR | Requires play-by-play data | BsR only reflects steals and double plays |

### Modeling

| Assumption | Reasoning | Effect |
|---|---|---|
| Target season has at least 100 PA | Removes pitcher-batting and tiny-sample noise | Predictions are conditional: injuries and lost jobs aren't forecast, and scores are slightly flattering |
| Only seasons from 1961 on, for targets and inputs | The expansion era has consistent records and matches the API cutoff | The first target season is 1962 |
| 2020 isn't used as a target | 60 games make counting stats incomparable | 2020 is still an input, so 2021–2023 predictions see an artificially low PA |
| Predicted oWAR divides by the player's last-season RPW | Next season's run environment is unknown | Small error when scoring changes year to year |

## Features

Each row predicts season N. There are 20 inputs, and none come from season N except age.

| Feature | Definition | Why it's included |
|---|---|---|
| `wRAA_l1..l3` | wRAA in each of the last 3 seasons | Recent hitting value |
| `BsR_l1..l3` | BsR in each of the last 3 seasons | Recent baserunning value |
| `RLR_l1..l3` | RLR in each of the last 3 seasons | Recent playing time and run environment |
| `PA_l1..l3` | PA in each of the last 3 seasons | Playing time and sample size |
| `wRAA_rate`, `BsR_rate` | Sum of weighted stat / (sum of weighted PA + 1200), weights 5/4/3 | Recent seasons count more, and small samples shrink toward average |
| `PA_expected` | 0.5 × PA_l1 + 0.1 × PA_l2 + 200 | Marcel's playing-time estimate |
| `RLR_rate_l1` | RLR_l1 / PA_l1 | Replacement value per PA |
| `Age_c`, `Age_c2` | Age in season N − 29, and its square | Aging is curved, with a peak in the late 20s |
| `has_l2`, `has_l3` | Whether that earlier season exists | Separates "no history" from a real zero |

The previous season must exist. Missing `l2` and `l3` values are filled with 0. Lags use calendar years, so a player who missed a full season has no `l1` and drops out.

## Models

Each candidate is trained separately for wRAA, BsR, and RLR. Parameters were set by hand and not searched, because the four candidates scored so closely that the inputs look like the limit.

### Baselines

| Baseline | Method | Purpose |
|---|---|---|
| Repeat last season | Predict last season's value | The simplest possible forecast |
| Marcel-style | Weighted rate from `wRAA_rate` or `BsR_rate` × `PA_expected`; for RLR, `RLR_rate_l1` × `PA_expected` | A standard, hard-to-beat public method. Omits Marcel's age adjustment |

### Gradient boosting (selected)

`HistGradientBoostingRegressor`

| Parameter | Value | Reasoning |
|---|---|---|
| `max_depth` | 4 | Allows feature interactions while limiting overfitting on noisy targets |
| `learning_rate` | 0.05 | Slower learning for steadier fits |
| `max_iter` | 200 | Enough rounds at this learning rate |
| `random_state` | 42 | Reproducibility |
| `early_stopping` | `auto` (default) | Active above 10,000 rows, so it holds out a random 10% and may stop before 200 rounds |
| Other settings | Defaults (31 leaf nodes, 20 samples per leaf, no L2) | Not tuned |

### Random forest

`RandomForestRegressor`

| Parameter | Value | Reasoning |
|---|---|---|
| `n_estimators` | 200 | Stable averages at a modest training cost |
| `min_samples_leaf` | 10 | Prevents memorizing rows; the original fully grown forests took about 350 MB each and scored 0.89 on training data against 0.23 on test |
| `random_state` | 42 | Reproducibility |

### Ridge regression

`StandardScaler` followed by `Ridge`

| Parameter | Value | Reasoning |
|---|---|---|
| `alpha` | 10.0 | Mild shrinkage, since the lag features are strongly correlated |

### Neural network

PyTorch `Sequential`, with inputs and target standardized

| Parameter | Value | Reasoning |
|---|---|---|
| Layers | 20 → 32 → 16 → 1 | Small network for about 20,000 rows |
| Activation | ReLU | Standard choice |
| Loss | MSE | Matches the other regressors |
| Optimizer | Adam, learning rate 0.005 | Lower than the original 0.01 for a steadier full-batch fit |
| `weight_decay` | 1e-3 | Regularization |
| Epochs | 400, full batch | Dataset fits in memory |
| Seed | 42 | Reproducibility |

## Evaluation design

| Split | Target seasons | Rows | Used for |
|---|---|---|---|
| Train | 1962–2009 | 16,667 | Fitting |
| Validation | 2010–2014 | 2,002 | Choosing a model per target |
| Test | 2015–2024, excluding 2020 | 3,603 | Final scores |

- **Time-based split:** a forecast must be trained only on the past. A random split would let later seasons inform earlier ones.
- **Selection on validation only:** the neural network scored slightly higher than gradient boosting on test for wRAA and RLR, but switching to it would have used test data to pick a winner.
- **Test fit:** models were retrained on train and validation before scoring on test.
- **Final fit:** the saved models were retrained on all 22,272 rows, so no separate score exists for those exact models.
- **Metrics:** R² compares across targets, and MAE gives the error in runs or wins.

## Results

### Validation R² (2010–2014)

| Model | wRAA | BsR | RLR |
|---|---|---|---|
| Gradient boosting | **0.346** | **0.343** | **0.463** |
| Ridge | 0.338 | 0.332 | 0.447 |
| Neural network | 0.337 | 0.334 | 0.458 |
| Random forest | 0.333 | 0.341 | 0.459 |

Gradient boosting won all three, by small margins.

### Test R² (2015–2024, excluding 2020)

| Method | oWAR | wRAA | BsR | RLR |
|---|---|---|---|---|
| Repeat last season | 0.139 | 0.082 | 0.006 | −0.179 |
| Marcel-style | 0.352 | 0.310 | 0.244 | 0.302 |
| Gradient boosting (selected) | **0.399** | 0.346 | 0.269 | 0.386 |
| Ridge | n/a | 0.339 | 0.260 | 0.390 |
| Random forest | n/a | 0.337 | 0.260 | 0.392 |
| Neural network | n/a | 0.348 | 0.247 | 0.410 |

oWAR is only computed for the selected combination and the baselines.

### Test MAE

| Method | oWAR (wins) | wRAA (runs) | BsR (runs) | RLR (runs) |
|---|---|---|---|---|
| Repeat last season | 1.22 | 9.89 | 0.99 | 4.48 |
| Marcel-style | 1.08 | 8.57 | 0.85 | 3.62 |
| Gradient boosting (selected) | 1.03 | 8.33 | 0.82 | 3.39 |

For full-time hitters (400+ PA, 1,777 rows), oWAR R² is 0.237, against 0.192 for Marcel-style. Full-time hitters are more alike, so there's less variation to explain.

## Key decisions

| Decision | Reasoning |
|---|---|
| Replace same-season models with next-season models | The original models used same-season inputs to estimate stats that are exact formulas, so they weren't forecasting anything |
| Don't feed target-season components as inputs | Adding them scored up to 1.000 only by relearning arithmetic; the original BsR's 0.86 fell to 0.02 without `wSB`, part of its own formula |
| Keep a separate model per component | The app shows each component, and oWAR follows directly from them |
| Compare against Marcel-style | Beating a simple public method is a more meaningful bar than a high R² |
| Accept R² near 0.4 | Next-season performance is noisy, and this is a true forecast measured on unseen seasons |
| Keep pre-1961 seasons in the viewable stats only | Older records are incomplete, but those players should remain browsable |
| Only predict for hitters active in the latest season | A retired player has no next season to forecast, so the API requires a row in the latest season and at least 100 PA over the last three |
| Keep live game data out of the models | The models expect completed seasons as inputs, so a partial season would look like a part-time player. In-season forecasting would need its own model |

## Limitations

- The model doesn't forecast playing time or injuries directly, and it only applies if the player reaches 100 PA.
- Forecasts are point estimates, with no uncertainty range.
- Inputs are limited to basic batting lines. Strikeouts, batted-ball quality, and Statcast data aren't used.
- Parameters weren't tuned.
- Projections shrink toward average by design, so star seasons are forecast well below their recent peaks.
- BsR dropped from 0.343 on validation to 0.269 on test, so it's the least stable target.
