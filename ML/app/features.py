import numpy as np
import pandas as pd

WOBA_SCALE = 1.25
RUN_SB = 0.2
REPLACEMENT_RATE = 0.235
FULL_SEASON_GAMES = 2430  # 162 * 30 / 2


def _col(df: pd.DataFrame, *names: str) -> str:
    lower = {str(col).lower(): col for col in df.columns}
    for name in names:
        if name in df.columns:
            return name
        key = name.lower()
        if key in lower:
            return lower[key]
    raise KeyError(f"None of {names} found in columns {list(df.columns)}")


def _frame(df: pd.DataFrame, mapping: dict[str, tuple[str, ...]]) -> pd.DataFrame:
    return pd.DataFrame({dest: df[_col(df, *src)] for dest, src in mapping.items()})


def compute_sabermetrics(player: pd.DataFrame, league: pd.DataFrame) -> pd.DataFrame:
    """Match ML.ipynb formulas so model inputs match training."""
    player_cols = _frame(
        player,
        {
            "idfg": ("idfg", "IDfg"),
            "season": ("season", "Season"),
            "age": ("age", "Age"),
            "pa": ("pa", "PA"),
            "gdp": ("gdp", "GDP"),
            "gdp_opp": ("gdp_opp", "GDP_OPP"),
            "sb": ("sb", "SB"),
            "cs": ("cs", "CS"),
            "bb": ("bb", "BB"),
            "hbp": ("hbp", "HBP"),
            "ibb": ("ibb", "IBB"),
            "woba": ("woba", "wOBA"),
            "1b": ("1B", "1b"),
        },
    )
    try:
        player_cols["name"] = player[_col(player, "name", "Name")]
    except KeyError:
        player_cols["name"] = None

    league_cols = _frame(
        league,
        {
            "season": ("season", "Season"),
            "pa": ("PA", "pa"),
            "rs": ("RS", "rs"),
            "ip": ("IP", "ip"),
            "gdp": ("GDP", "gdp"),
            "gdp_opp": ("GDP_OPP", "gdp_opp"),
            "sb": ("SB", "sb"),
            "cs": ("CS", "cs"),
            "bb": ("BB", "bb"),
            "hbp": ("HBP", "hbp"),
            "ibb": ("IBB", "ibb"),
            "league_woba": ("league_wOBA", "league_woba"),
            "1b": ("1B", "1b"),
        },
    )

    combined = player_cols.merge(league_cols, on="season", suffixes=("_player", "_league"))
    if combined.empty:
        return combined

    pa = combined["pa_player"]
    league_pa = combined["pa_league"]
    rs = combined["rs"]
    ip = combined["ip"]
    outs = ip * 3

    run_cs = (-2 * (rs / outs)) + 0.075
    w_gdp = (
        ((combined["gdp_league"] / combined["gdp_opp_league"]) * combined["gdp_opp_player"])
        - combined["gdp_player"]
    ) * (rs / outs)
    league_wsb = ((combined["sb_league"] * RUN_SB) + (combined["cs_league"] * run_cs)) / (
        combined["1b_league"] + combined["bb_league"] + combined["hbp_league"] + combined["ibb_league"]
    )
    w_sb = ((combined["sb_player"] * RUN_SB) + (combined["cs_player"] * run_cs)) - (
        league_wsb
        * (
            combined["1b_player"]
            + combined["bb_player"]
            + combined["hbp_player"]
            + combined["ibb_player"]
        )
    )
    bsr = w_sb + w_gdp
    rpw = (9 * (rs / outs) * 1.5) + 3
    rlr = (REPLACEMENT_RATE * FULL_SEASON_GAMES * rpw * pa) / league_pa
    wraa = ((combined["woba"] - combined["league_woba"]) / WOBA_SCALE) * pa

    out = pd.DataFrame(
        {
            "idfg": combined["idfg"],
            "name": combined["name"],
            "Age": combined["age"],
            "Season": combined["season"],
            "wRAA": wraa,
            "BsR": bsr,
            "RLR": rlr,
            "wGDP": w_gdp,
            "runCS": run_cs,
            "league_wSB": league_wsb,
            "wSB": w_sb,
            "RPW": rpw,
        }
    )
    out = out.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["Age", "wRAA", "BsR", "RLR", "wGDP", "runCS", "league_wSB", "wSB", "RPW"]
    )
    return out.sort_values("Season").reset_index(drop=True)
