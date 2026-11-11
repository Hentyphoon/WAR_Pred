import numpy as np
import pandas as pd

LAG_STATS = ["wRAA", "BsR", "RLR", "PA"]
WEIGHTS = {1: 5, 2: 4, 3: 3}

FEATURES = [
    "Age_c", "Age_c2", "has_l2", "has_l3",
    "wRAA_rate", "BsR_rate", "PA_expected", "RLR_rate_l1",
    *[f"{s}_l{k}" for k in WEIGHTS for s in LAG_STATS],
]


def add_history(rows: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    """Add features for each (IDfg, Season, Age) row from the three seasons before it."""
    out = rows.copy()
    for k in WEIGHTS:
        lag = history[["IDfg", "Season", *LAG_STATS, "RPW", "oWAR"]].copy()
        lag["Season"] += k
        out = out.merge(
            lag.rename(columns={c: f"{c}_l{k}" for c in [*LAG_STATS, "RPW", "oWAR"]}),
            on=["IDfg", "Season"],
            how="left",
        )
    out = out[out["PA_l1"].notna()].copy()

    for k in (2, 3):
        out[f"has_l{k}"] = out[f"PA_l{k}"].notna().astype(int)
    for c in [f"{s}_l{k}" for k in WEIGHTS for s in LAG_STATS]:
        out[c] = out[c].fillna(0)

    weighted_pa = sum(w * out[f"PA_l{k}"] for k, w in WEIGHTS.items())
    for s in ["wRAA", "BsR"]:  # regressed toward league average with 1200 PA of ballast, as in Marcel
        out[f"{s}_rate"] = sum(w * out[f"{s}_l{k}"] for k, w in WEIGHTS.items()) / (weighted_pa + 1200)
    out["PA_expected"] = 0.5 * out["PA_l1"] + 0.1 * out["PA_l2"] + 200
    out["RLR_rate_l1"] = (out["RLR_l1"] / out["PA_l1"].replace(0, np.nan)).fillna(0)
    out["Age_c"] = out["Age"] - 29
    out["Age_c2"] = out["Age_c"] ** 2
    return out
