import os
from pathlib import Path

import joblib
import torch
import torch.nn as nn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).parent.parent / ".env")  # ml/app/main.py -> ml/.env

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_methods=["GET"],
    allow_headers=["*"],
)

MODEL_DIR = Path(__file__).parent / "model"



def make_wraa_model() -> nn.Module:
    # trained on: ['Age', 'BsR', 'wSB', 'RLR', 'wGDP']  (5 features)
    return nn.Sequential(
        nn.Linear(5, 16),
        nn.ReLU(),
        nn.Linear(16, 16),
        nn.ReLU(),
        nn.Linear(16, 1),
    )


def make_bsr_model() -> nn.Module:
    # trained on: ['wSB', 'runCS', 'league_wSB']  (3 features)
    return nn.Sequential(
        nn.Linear(3, 16),
        nn.ReLU(),
        nn.Linear(16, 16),
        nn.ReLU(),
        nn.Linear(16, 1),
    )


def make_rlr_model() -> nn.Module:
    # trained on: ['Age', 'RPW', 'league_wSB', 'wGDP']  (4 features)
    return nn.Sequential(
        nn.Linear(4, 16),
        nn.ReLU(),
        nn.Linear(16, 16),
        nn.ReLU(),
        nn.Linear(16, 1),
    )


def load_torch_model(builder, filename: str) -> nn.Module:
    model = builder()
    state_dict = torch.load(MODEL_DIR / filename, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    return model


wraa_model = load_torch_model(make_wraa_model, "wraa_model.pth")
bsr_model = load_torch_model(make_bsr_model, "bsr_model.pth")
rlr_model = load_torch_model(make_rlr_model, "rlr_model.pth")


scaler_X_wraa = joblib.load(MODEL_DIR / "scaler_X_wraa.pkl")
scaler_X_rlr = joblib.load(MODEL_DIR / "scaler_X_rlr.pkl")
scaler_X_bsr = joblib.load(MODEL_DIR / "scaler_X_bsr.pkl")
scaler_y_wraa = joblib.load(MODEL_DIR / "scaler_y_wraa.pkl")
scaler_y_bsr = joblib.load(MODEL_DIR / "scaler_y_bsr.pkl")
scaler_y_rlr = joblib.load(MODEL_DIR / "scaler_y_rlr.pkl")


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Either export it in your shell "
        "(export DATABASE_URL=...) or add it to a .env file in this "
        "directory, same as the training notebook does."
    )
engine = create_engine(DATABASE_URL)
print(f"[DEBUG] Using DATABASE_URL: {DATABASE_URL}")  # TEMP - remove after debugging


SABERMETRIC_QUERY = text(
    """
    SELECT "Age", "BsR", "wSB", "RLR", "wGDP", "runCS", "league_wSB", "RPW"
    FROM playersabermetric
    WHERE "IDfg" = :idfg
    ORDER BY "Season" DESC
    LIMIT 1
    """
)


def get_sabermetric_row(idfg: str) -> dict[str, float]:
    """
    Look up the most recent season's sabermetric components for a player
    from the playersabermetric table (built in the training notebook).
    """
    with engine.connect() as conn:
        row = conn.execute(SABERMETRIC_QUERY, {"idfg": idfg}).mappings().fetchone()

    if row is None:
        raise LookupError(f"No playersabermetric row found for IDfg={idfg}")

    return {k: float(v) for k, v in row.items()}


def predict_one(model: nn.Module, scaler_X, scaler_y, x_ordered: list[float]) -> float:
    x_scaled = scaler_X.transform([x_ordered])
    x_tensor = torch.tensor(x_scaled, dtype=torch.float32)

    with torch.no_grad():
        y_scaled = model(x_tensor).numpy()

    y = scaler_y.inverse_transform(y_scaled)
    return float(y[0, 0])


@app.get("/prediction/{idfg}")
def get_prediction(idfg: str):
    try:
        row = get_sabermetric_row(idfg)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    wraa = predict_one(
        wraa_model,
        scaler_X_wraa,
        scaler_y_wraa,
        [row["Age"], row["BsR"], row["wSB"], row["RLR"], row["wGDP"]],
    )
    bsr = predict_one(
        bsr_model,
        scaler_X_bsr,
        scaler_y_bsr,
        [row["wSB"], row["runCS"], row["league_wSB"]],
    )
    rlr = predict_one(
        rlr_model,
        scaler_X_rlr,
        scaler_y_rlr,
        [row["Age"], row["RPW"], row["league_wSB"], row["wGDP"]],
    )

    return {
        "idfg": idfg,
        "prediction": {
            "bsr": bsr,
            "wraa": wraa,
            "rlr": rlr,
        },
    }