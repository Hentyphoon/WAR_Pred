import numpy as np
import pandas as pd
import pytest

from cleaner import DataCleaner

BATTING = ["IDfg", "Season", "stint", "teamID", "lgID", "G", "AB", "R", "H", "2B", "3B", "HR",
           "RBI", "SB", "CS", "BB", "SO", "IBB", "HBP", "SH", "SF", "GDP"]


def batting(idfg, season, stint=1, **stats):
    row = {col: 0 for col in BATTING}
    row.update({"IDfg": idfg, "Season": season, "stint": stint, "teamID": "T1", "lgID": "AL"})
    row.update(stats)
    return row


@pytest.fixture
def write_csvs(tmp_path, monkeypatch):
    """Write the three source CSVs into a temp dir, which the cleaner reads from the working directory."""
    monkeypatch.chdir(tmp_path)

    def write(rows):
        pd.DataFrame(rows, columns=BATTING).to_csv("Batting.csv", index=False)
        ids = sorted({r["IDfg"] for r in rows})
        pd.DataFrame(
            {"IDfg": ids, "nameFirst": "First", "nameLast": ids, "birthYear": 1990}
        ).to_csv("People.csv", index=False)
        seasons = sorted({r["Season"] for r in rows})
        pd.DataFrame(
            {"playerID": "pitcher", "Season": seasons, "G": 10, "IPouts": 2700}
        ).to_csv("Pitching.csv", index=False)

    return write


def test_blank_early_era_stats_do_not_erase_plate_appearances(write_csvs):
    # 1921-style row: sacrifice flies and intentional walks weren't recorded
    write_csvs([batting("ruth", 1921, AB=540, H=204, BB=145, HBP=4, SH=4, SF=np.nan, IBB=np.nan, CS=np.nan, GDP=np.nan)])
    row = DataCleaner().load_player_stats().iloc[0]
    assert row["PA"] == 540 + 145 + 4 + 4
    assert row["UBB"] == 145
    assert not np.isnan(row["wOBA"])


def test_intentional_walks_are_left_out_of_woba(write_csvs):
    write_csvs([batting("a", 2004, AB=100, BB=50, IBB=40)])
    row = DataCleaner().load_player_stats().iloc[0]
    # only the 10 unintentional walks count, in the numerator and the denominator
    assert row["wOBA"] == pytest.approx(10 * 0.69 / (100 + 10))


def test_multi_team_seasons_are_summed(write_csvs):
    write_csvs([
        batting("a", 2010, stint=1, AB=200, H=50, HR=5),
        batting("a", 2010, stint=2, AB=100, H=30, HR=3),
    ])
    player = DataCleaner().load_player_stats()
    assert len(player) == 1
    assert player.iloc[0]["AB"] == 300
    assert player.iloc[0]["HR"] == 8


def test_season_without_plate_appearances_has_no_woba(write_csvs):
    write_csvs([batting("pitcher", 2010), batting("hitter", 2010, AB=10, H=3)])
    player = DataCleaner().load_player_stats().set_index("IDfg")
    assert np.isnan(player.loc["pitcher", "wOBA"])


def test_intentional_walk_only_season_has_no_infinite_woba(write_csvs):
    write_csvs([batting("a", 2010, BB=1, IBB=1), batting("b", 2010, AB=10, H=3)])
    player = DataCleaner().load_player_stats().set_index("IDfg")
    assert not np.isinf(player.loc["a", "wOBA"])


def test_age_comes_from_birth_year(write_csvs):
    write_csvs([batting("a", 2020, AB=10)])
    assert DataCleaner().load_player_stats().iloc[0]["Age"] == 30


def test_league_totals_fill_blank_stats_and_count_innings(write_csvs):
    write_csvs([
        batting("a", 1921, AB=500, H=150, BB=50, HBP=5, SF=np.nan, SH=np.nan, IBB=np.nan),
        batting("b", 1921, AB=400, H=100, BB=40, HBP=2, SF=np.nan, SH=np.nan, IBB=np.nan),
    ])
    league = DataCleaner().load_league_stats().iloc[0]
    assert league["PA"] == 500 + 50 + 5 + 400 + 40 + 2
    assert league["IP"] == 900
    assert 0 < league["league_wOBA"] < 1
