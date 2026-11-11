import json
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

from app.features import FEATURES, add_history

load_dotenv(Path(__file__).parent.parent / ".env")  # ml/app/main.py -> ml/.env

MODEL_DIR = Path(__file__).parent / "model"
MIN_RECENT_PA = 100
TARGETS = ["wRAA", "BsR", "RLR"]


@lru_cache
def load_models() -> tuple[int, dict]:
    """Return the last season of training data and a model per target."""
    metadata = json.loads((MODEL_DIR / "metadata.json").read_text())
    return metadata["data_through"], {target: joblib.load(MODEL_DIR / f"{target}.joblib") for target in TARGETS}


@lru_cache
def get_engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Either export it in your shell "
            "(export DATABASE_URL=...) or add it to a .env file in this "
            "directory, same as the training notebook does."
        )
    return create_engine(database_url)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Fail at startup, not on the first request, if models or config are missing.
    load_models()
    get_engine()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_methods=["GET"],
    allow_headers=["*"],
)


HISTORY_QUERY = text(
    """
    SELECT "IDfg", "Season", "Age", "PA", "wRAA", "BsR", "RLR", "RPW", "oWAR"
    FROM playersabermetric
    WHERE "IDfg" = :idfg AND "Season" BETWEEN :first_season AND :last_season
    """
)


def load_history(idfg: str, first_season: int, last_season: int) -> pd.DataFrame:
    return pd.read_sql(
        HISTORY_QUERY,
        get_engine(),
        params={"idfg": idfg, "first_season": first_season, "last_season": last_season},
    )


def get_features(idfg: str, data_through: int) -> pd.DataFrame:
    """Build next-season model inputs for a player active in the latest season."""
    history = load_history(idfg, data_through - 2, data_through)
    latest = history[history["Season"] == data_through]

    if latest.empty or history["PA"].sum() < MIN_RECENT_PA:
        raise LookupError(
            f"No prediction available. Predictions only cover hitters active in {data_through} "
            f"with at least {MIN_RECENT_PA} PA over the last three seasons."
        )

    target = pd.DataFrame(
        [{"IDfg": idfg, "Season": data_through + 1, "Age": float(latest["Age"].iloc[0]) + 1}]
    )
    return add_history(target, history)


@app.get("/prediction/{idfg}")
def get_prediction(idfg: str):
    data_through, models = load_models()
    try:
        features = get_features(idfg, data_through)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    predicted = {target: float(models[target].predict(features[FEATURES])[0]) for target in TARGETS}

    return {
        "idfg": idfg,
        "season": data_through + 1,
        "prediction": {
            "bsr": predicted["BsR"],
            "wraa": predicted["wRAA"],
            "rlr": predicted["RLR"],
            "owar": sum(predicted.values()) / float(features["RPW_l1"].iloc[0]),
        },
    }
