import pandas as pd
import pytest

from app.features import FEATURES, add_history


def season(idfg, year, pa, wraa=0.0, bsr=0.0, rlr=0.0, rpw=10.0):
    return {"IDfg": idfg, "Season": year, "PA": pa, "wRAA": wraa, "BsR": bsr, "RLR": rlr, "RPW": rpw, "oWAR": 0.0}


def target(idfg, year, age):
    return pd.DataFrame([{"IDfg": idfg, "Season": year, "Age": age}])


def test_builds_every_model_feature():
    history = pd.DataFrame([season("a", 2024, 600, wraa=30)])
    out = add_history(target("a", 2025, 30), history)
    assert set(FEATURES) <= set(out.columns)
    assert not out[FEATURES].isna().any().any()


def test_drops_rows_without_previous_season():
    history = pd.DataFrame([season("a", 2022, 600)])  # 2023 missing, so no l1 for 2024
    assert add_history(target("a", 2024, 30), history).empty


def test_marks_missing_older_seasons_and_fills_zero():
    history = pd.DataFrame([season("a", 2024, 500, wraa=10)])
    row = add_history(target("a", 2025, 25), history).iloc[0]
    assert row["has_l2"] == 0
    assert row["has_l3"] == 0
    assert row["PA_l2"] == 0
    assert row["wRAA_l3"] == 0


def test_weights_recent_seasons_and_regresses_to_average():
    history = pd.DataFrame(
        [season("a", 2024, 600, wraa=30), season("a", 2023, 600, wraa=0), season("a", 2022, 600, wraa=0)]
    )
    row = add_history(target("a", 2025, 29), history).iloc[0]
    # 5*30 / (5*600 + 4*600 + 3*600 + 1200)
    assert row["wRAA_rate"] == pytest.approx(150 / 8400)
    assert row["PA_expected"] == pytest.approx(0.5 * 600 + 0.1 * 600 + 200)


def test_centers_age_on_29():
    history = pd.DataFrame([season("a", 2024, 500)])
    row = add_history(target("a", 2025, 32), history).iloc[0]
    assert row["Age_c"] == 3
    assert row["Age_c2"] == 9


def test_replacement_rate_handles_zero_pa():
    history = pd.DataFrame([season("a", 2024, 0, rlr=0)])
    row = add_history(target("a", 2025, 30), history).iloc[0]
    assert row["RLR_rate_l1"] == 0


def test_keeps_players_separate():
    history = pd.DataFrame([season("a", 2024, 600, wraa=40), season("b", 2024, 600, wraa=-10)])
    rows = pd.concat([target("a", 2025, 30), target("b", 2025, 30)])
    out = add_history(rows, history).set_index("IDfg")
    assert out.loc["a", "wRAA_l1"] == 40
    assert out.loc["b", "wRAA_l1"] == -10
