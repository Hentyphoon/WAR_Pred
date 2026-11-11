# WAR_pred

Look up any MLB hitter's season stats and forecast their offensive value for next season.

WAR_pred combines a searchable database of batting seasons from 1871 to 2024 with machine learning models that project a hitter's next-season offensive WAR (oWAR) and its components: wRAA, BsR, and RLR.

## Features

- Search for players by name, with a list to choose from when several match
- Browse season-by-season stats for players from every era
- Get next-season predictions for active hitters

## Model results

Scores come from seasons the models never saw during training or selection: 2015–2024, excluding the shortened 2020 season.

| Method | oWAR R² | oWAR mean error (wins) |
|---|---|---|
| Repeat last season | 0.139 | 1.22 |
| Marcel-style baseline | 0.352 | 1.08 |
| **WAR_pred (gradient boosting)** | **0.399** | **1.03** |

Marcel is a simple public forecasting method that's hard to beat. Projections assume the player reaches at least 100 PA next season. oWAR excludes fielding, so it will differ from published WAR.

See [models.md](models.md) for formulas, features, parameters, and reasoning.

## How it works

```text
Batting, pitching, and people CSVs
        |
        v
Migration/  cleans the data and loads player and league stats
        |
        v
PostgreSQL
   |                         |
   v                         v
Backend/ (Express)      ML/ (FastAPI + models)
stats and search        predictions
   |                         |
   +----------+--------------+
              v
      Frontend/ (React)
```

| Directory | Purpose | Stack |
|---|---|---|
| `Frontend/` | Search, player, and prediction pages | React, TypeScript, Vite |
| `Backend/` | Player stats and search API | Node.js, Express, PostgreSQL |
| `ML/` | Prediction API, training notebook | FastAPI, PyTorch, scikit-learn |
| `Migration/` | Data cleaning and database load | Python, pandas |
| `Live/` | Live game event pipeline (planned, skeleton only) | Python, Apache Kafka |
| `docs/` | Project documentation | |

## Getting started

### Prerequisites

- Node.js and npm
- Python 3.13 (the `npm run dev` script calls the Windows `py -3` launcher)
- A PostgreSQL database

### 1. Install dependencies

```bash
npm install
npm install --prefix Backend
npm install --prefix Frontend
py -3 -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs the ML requirements plus the test tools. Use `ML/requirements.txt` alone if you don't need the tests.

### 2. Configure environment variables

Create these three files, which are gitignored:

| File | Variable | Value |
|---|---|---|
| `Backend/.env` | `DATABASE_URL` | PostgreSQL connection string |
| `ML/.env` | `DATABASE_URL` | PostgreSQL connection string |
| `Frontend/.env` | `VITE_API_URL` | `http://localhost:8000` |
| `Frontend/.env` | `VITE_PREDICTION_API_URL` | `http://localhost:8001` |

### 3. Build the data and models

```bash
cd Migration
py -3 main.py
```

Then run `ML/notebook/ML.ipynb` from top to bottom in VS Code or Jupyter. Together these create the database tables and the models in `ML/app/model/`.

### 4. Start the app

```bash
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Stats API | http://localhost:8000 |
| Prediction API | http://localhost:8001 |

## Running tests

```bash
npm test
```

This runs every suite. None of them need a database, trained models, or network access.

| Suite | Command | Tool | Covers |
|---|---|---|---|
| Backend | `npm test --prefix Backend` | Node test runner | Search and player routes, with the database mocked |
| Frontend | `npm test --prefix Frontend` | Vitest, Testing Library | Missing stats, search results, and prediction errors |
| Python | `npm run test:py` | pytest | Data cleaning, model features, and the prediction API with mocked models |

## API reference

| Service | Endpoint | Description |
|---|---|---|
| Stats | `GET /search?q={name}` | Up to 10 players matching the name, with first and last seasons |
| Stats | `GET /players/{id}` | All of a player's seasons, oldest first |
| Prediction | `GET /prediction/{id}` | Next-season BsR, wRAA, RLR, and oWAR. Returns 404 unless the player was active in the latest season, with at least 100 PA over the last three seasons |

## Current limitations

- **The data ends in 2024,** so predictions are for the 2025 season.
- **The predictions page doesn't show oWAR yet,** although the API returns it.
- **The models don't forecast injuries or playing time directly,** and predictions have no uncertainty range.

## Live game pipeline (planned)

`Live/` holds the skeleton for an event pipeline that follows games in progress. None of its logic is written yet.

```text
MLB live feed
   | polled at the feed's suggested interval, only for games in progress
producer -> Kafka topics: plays, pitches
              |-> ticker          prints plays to the terminal
              |-> store           upserts into live_plays and live_pitches
              '-> home_run_alert  sends one notification per home run
```

Each consumer reads the same stream in its own consumer group, so one failing doesn't affect the others. Plays can be revised after the fact, and Kafka can redeliver messages, so consumers must handle corrections and duplicates.

| Stage | Work | Depends on |
|---|---|---|
| 1 | Producer and the three consumers | Docker, to run Kafka |
| 2 | Live games API and page | Stage 1 |
| 3 | Per-game batting lines that update season totals automatically | Stage 1, MLB-to-local player ID mapping, 2025–2026 backfill |

Predictions stay on completed seasons and don't change during games.

The pipeline only runs against games in progress. For testing outside the season, recorded game feeds can be run through it. Those recordings go in `Live/test_data/`, which is gitignored, and replay isn't a feature of the app.

The feed comes from MLB's free, unofficial Stats API. Its responses link to MLB's copyright terms, which should be reviewed before hosting a public demo.

## Documentation

- [models.md](models.md): how the models work and why they were built this way
- [design.md](design.md): direction for future UI work
