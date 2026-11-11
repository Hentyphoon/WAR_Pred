import os
from pathlib import Path

from cleaner import DataCleaner
from dotenv import load_dotenv
from sqlalchemy import Integer, create_engine, text

load_dotenv(Path(__file__).parent.parent / "ML" / ".env")

PLAYER_COLUMNS = {
    "IDfg": "idfg", "Name": "name", "Season": "season", "Age": "age", "PA": "pa",
    "AB": "ab", "H": "h", "HR": "hr", "BB": "bb", "IBB": "ibb", "UBB": "ubb",
    "HBP": "hbp", "SB": "sb", "CS": "cs", "GDP": "gdp", "GDP_OPP": "gdp_opp",
    "SF": "sf", "wOBA": "woba",
}
PLAYER_INTEGER_COLUMNS = ["season", "ab", "h", "1B", "2B", "3B", "hr", "bb"]  # node-pg returns BIGINT as strings


def main():
    cleaner = DataCleaner()
    player = cleaner.load_player_stats().rename(columns=PLAYER_COLUMNS)
    league = cleaner.load_league_stats()

    engine = create_engine(os.environ["DATABASE_URL"])
    player.to_sql(
        "playerstat",
        engine,
        if_exists="replace",
        index=False,
        dtype={col: Integer() for col in PLAYER_INTEGER_COLUMNS},
    )
    league.to_sql("leaguestat", engine, if_exists="replace", index=False)
    with engine.begin() as conn:  # to_sql drops the existing keys
        conn.execute(text('ALTER TABLE playerstat ADD PRIMARY KEY (idfg, season)'))
        conn.execute(text('ALTER TABLE leaguestat ADD PRIMARY KEY ("Season")'))
    print(f"Loaded {len(player)} player seasons and {len(league)} league seasons")


main()
