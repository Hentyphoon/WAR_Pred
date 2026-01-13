'''
Required Stats
player
PA, 1B, 2B, 3B, HR, UBB, HBP, SB, CS(caught stealing), GDP(double play), GDP opportunities, SF(Sacrifice Fly), Innings played at each position
league
INN/G, PA, RS(Runs Scored), IP, G, 1B, BB, HBP, IBB, SB, CS, GDP, GDP opportunities, league wOBA

IMPORTANT: GDP opportunities and league wOBA is estimated for this project
UPDATE: Since no fielding stats are provided by pybaseball for positions played, only offensive fWAR will be calculated.
'''

import pandas as pd
import numpy as np
from pybaseball import batting_stats, fielding_stats, pitching_stats
import datetime as dt
import time


def load_player_stats(name):
    df = batting_stats(start_season=2021,end_season = dt.datetime.now().year - 1, qual=1)
    player_df = df[df["Name"].str.lower() == name.lower()].copy()

    if player_df.empty:
        raise ValueError(f"No data found for player: {name}")
    
    player_df = player_df[[
        "IDfg", "Name", "Season",
        "PA", "H", "2B", "3B", "HR",
        "BB", "IBB", "HBP",
        "SB", "CS",
        "GDP", "SF","Age"
    ]]

    player_df["1B"] = df["H"] - df["2B"] - df["3B"] - df["HR"]
    player_df["UBB"] = df["BB"] - df["IBB"]
    player_df["GDP_OPP"] = (
        df["PA"]
        - df["HR"]
        - df["BB"]
        - df["HBP"]
        - df["SF"]
    )
    weights = {
        "BB": 0.69,
        "HBP": 0.72,
        "1B": 0.88,
        "2B": 1.247,
        "3B": 1.578,
        "HR": 2.031
    }
    numerator = (
        player_df["BB"] * weights["BB"]
        + player_df["HBP"] * weights["HBP"]
        + player_df["1B"] * weights["1B"]
        + player_df["2B"] * weights["2B"]
        + player_df["3B"] * weights["3B"]
        + player_df["HR"] * weights["HR"]
    )

    denominator = player_df["AB"] + player_df["UBB"] + player_df["HBP"] + player_df["SF"]
    player_df["wOBA"] = numerator / denominator

    return player_df

def load_league_stats():
    bat = batting_stats(start_season=2021,end_season = dt.datetime.now().year - 1, qual=1)
    bat["1B"] = bat["H"] - bat["2B"] - bat["3B"] - bat["HR"]
    bat["GDP_OPP"] = (
        bat["PA"]
        - bat["HR"]
        - bat["BB"]
        - bat["HBP"]
        - bat["SF"]
    )

    league_bat = (
        bat
        .groupby("Season")
        .agg({
            "PA": "sum",
            "R": "sum",          
            "1B": "sum",
            "BB": "sum",
            "IBB": "sum",
            "HBP": "sum",
            "SB": "sum",
            "CS": "sum",
            "GDP": "sum",
            "GDP_OPP": "sum",
            "2B": "sum",
            "3B": "sum",
            "HR": "sum",
            "AB":"sum",
            "UBB":"sum"
        })
        .reset_index()
        .rename(columns={"R": "RS"})
    )
    pitch = pitching_stats(start_season=2021,end_season = dt.datetime.now().year - 1, qual=0)

    league_pitch = (
        pitch
        .groupby("Season")
        .reset_index()
    )
    league_pitch["G"] = 2430  # Total games in a MLB season, assuming no cancellations, also we start from 2021 because COVID made MLB shorter
    weights = {
        "BB": 0.69,
        "HBP": 0.72,
        "1B": 0.88,
        "2B": 1.247,
        "3B": 1.578,
        "HR": 2.031
    }
    league_pitch["INN_per_G"] = 9 
    # Average innings per game, assuming full 9 innings games, since pybaseball does not provide this directly I would need to add all IP and divide by G
    # so for simplicity, we assume full games
    league = league_bat.merge(league_pitch, on="Season", how="left")
    numerator = (
        league["BB"] * weights["BB"]
        + league["HBP"] * weights["HBP"]
        + league["1B"] * weights["1B"]
        + league["2B"] * weights["2B"]
        + league["3B"] * weights["3B"]
        + league["HR"] * weights["HR"]
    )

    denominator = league["AB"] + league["UBB"] + league["HBP"] + league["SF"]
    league["league_wOBA"] = numerator / denominator
    league = league[[
        "Season",
        "INN_per_G",
        "PA",
        "RS",
        "IP",
        "G",
        "1B",
        "BB",
        "HBP",
        "IBB",
        "SB",
        "CS",
        "GDP",
        "GDP_OPP",
        "league_wOBA"
    ]]

    return league.sort_values("Season")

