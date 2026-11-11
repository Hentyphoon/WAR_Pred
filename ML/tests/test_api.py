import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.features import FEATURES

DATA_THROUGH = 2024


class FakeModel:
    def __init__(self, value):
        self.value = value
        self.columns = None

    def predict(self, X):
        self.columns = list(X.columns)
        return np.array([self.value])


def season(year, pa, age=30.0, rpw=10.0):
    return {"IDfg": "p1", "Season": year, "Age": age, "PA": pa, "wRAA": 5.0, "BsR": 1.0, "RLR": 10.0, "RPW": rpw, "oWAR": 1.6}


@pytest.fixture
def models():
    return {"wRAA": FakeModel(20.0), "BsR": FakeModel(2.0), "RLR": FakeModel(18.0)}


@pytest.fixture
def client(monkeypatch, models):
    history = {}
    monkeypatch.setattr(main, "load_models", lambda: (DATA_THROUGH, models))
    monkeypatch.setattr(main, "load_history", lambda idfg, first, last: pd.DataFrame(history.get(idfg, []), columns=list(season(0, 0))))
    test_client = TestClient(main.app)  # not entered as a context, so startup doesn't touch real models or the DB
    test_client.history = history
    return test_client


def test_predicts_next_season_for_active_player(client, models):
    client.history["p1"] = [season(2024, 600, rpw=10.0), season(2023, 550)]
    response = client.get("/prediction/p1")

    assert response.status_code == 200
    body = response.json()
    assert body["season"] == 2025
    assert body["prediction"]["wraa"] == 20.0
    assert body["prediction"]["bsr"] == 2.0
    assert body["prediction"]["rlr"] == 18.0
    assert body["prediction"]["owar"] == pytest.approx((20 + 2 + 18) / 10.0)
    assert models["wRAA"].columns == FEATURES


def test_rejects_retired_player(client):
    client.history["p1"] = [season(2023, 600)]  # nothing in the latest season
    response = client.get("/prediction/p1")
    assert response.status_code == 404
    assert "active in 2024" in response.json()["detail"]


def test_rejects_player_with_too_little_playing_time(client):
    client.history["p1"] = [season(2024, 40), season(2023, 30)]
    assert client.get("/prediction/p1").status_code == 404


def test_rejects_unknown_player(client):
    assert client.get("/prediction/nobody").status_code == 404


def test_uses_age_in_the_predicted_season(client, monkeypatch):
    client.history["p1"] = [season(2024, 600, age=33.0)]
    captured = {}
    original = main.add_history

    def spy(rows, history):
        captured["age"] = rows["Age"].iloc[0]
        return original(rows, history)

    monkeypatch.setattr(main, "add_history", spy)
    client.get("/prediction/p1")
    assert captured["age"] == 34.0


def test_missing_database_url_fails_clearly(monkeypatch):
    main.get_engine.cache_clear()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        main.get_engine()
    main.get_engine.cache_clear()
