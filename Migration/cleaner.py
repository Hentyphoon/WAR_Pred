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


class DataCleaner: #load 
    def load_player_stats(self):
        player_df = pd.read_csv("Batting.csv")
        people_df = pd.read_csv("People.csv")

        people_df["Name"] = people_df["nameFirst"] + " " + people_df["nameLast"]
        player_df = player_df.merge(people_df[["IDfg", "Name", "birthYear"]], on="IDfg", how="left")

        player_df["PA"] = (
            player_df["AB"]
            + player_df["BB"]
            + player_df["HBP"]
            + player_df["SF"]
            + player_df["SH"]
        )
        player_df["1B"] = player_df["H"] - player_df["2B"] - player_df["3B"] - player_df["HR"]
        player_df["UBB"] = player_df["BB"] - player_df["IBB"]
        player_df["GDP_OPP"] = (
            player_df["PA"]
            - player_df["HR"]
            - player_df["BB"]
            - player_df["HBP"]
            - player_df["SF"]
        )
        player_df["Age"] = player_df["Season"] - player_df["birthYear"]
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

        player_df = player_df[[
            "IDfg", "Name", "Season", "Age",
            "PA", "AB", "H", "1B", "2B", "3B", "HR",
            "BB", "IBB", "UBB", "HBP",
            "SB", "CS",
            "GDP", "GDP_OPP", "SF", "wOBA"
        ]]

        player_df.to_csv("PlayerStat.csv", index=False) 

    def load_league_stats(self): #load all league stat
        bat = pd.read_csv("Batting.csv")
        bat["1B"] = bat["H"] - bat["2B"] - bat["3B"] - bat["HR"]
        bat["UBB"] = bat["BB"] - bat["IBB"]
        bat["PA"] = (
            bat["AB"]
            + bat["BB"]
            + bat["HBP"].fillna(0)
            + bat["SF"].fillna(0)
            + bat["SH"].fillna(0)
        )
        bat["GDP_OPP"] = (
            bat["PA"]
            - bat["HR"]
            - bat["BB"]
            - bat["HBP"].fillna(0)
            - bat["SF"].fillna(0)
        )

        league_bat = (
            bat
            .groupby("Season")
            .agg({
                "PA": "sum",
                "R": "sum",
                "AB": "sum",
                "1B": "sum",
                "BB": "sum",
                "IBB": "sum",
                "UBB": "sum",
                "HBP": "sum",
                "SF": "sum",     
                "SB": "sum",
                "CS": "sum",
                "GDP": "sum",
                "GDP_OPP": "sum",
                "2B": "sum",
                "3B": "sum",
                "HR": "sum",
            })
            .reset_index()
            .rename(columns={"R": "RS"})
        )

        pitch = pd.read_csv("Pitching.csv")
        pitch["IP"] = pitch["IPouts"]/3 #account for partial innings
        league_pitch = (          
            pitch
            .groupby("Season")
            .agg({"IP": "sum"})
        )
        league_pitch["G"] = pitch.groupby("Season")["G"].sum().values
        league_pitch["INN_per_G"] = league_pitch["IP"] / league_pitch["G"]
        

        league = league_bat.merge(league_pitch, on="Season", how="left")

        weights = {
            "BB": 0.69, "HBP": 0.72, "1B": 0.88,
            "2B": 1.247, "3B": 1.578, "HR": 2.031
        }
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
            "Season", "INN_per_G", "PA", "RS", "IP", "G",
            "1B", "BB", "IBB", "HBP",
            "SB", "CS",
            "GDP", "GDP_OPP", "league_wOBA"  
        ]]

        league.to_csv("LeagueStat.csv", index=False)  
def main():
    cleaner = DataCleaner()
    league_df = cleaner.load_league_stats()
    player_df = cleaner.load_player_stats()
    print("meow")
main()