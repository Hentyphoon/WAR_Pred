'''
Required Stats
player
PA, 1B, 2B, 3B, HR, UBB, HBP, SB, CS(caught stealing), GDP(double play), GDP opportunities, SF(Sacrifice Fly), Innings played at each position
league
INN/G, PA, RS(Runs Scored), IP, G, 1B, BB, HBP, IBB, SB, CS, GDP, GDP opportunities, league wOBA

IMPORTANT: GDP opportunities and league wOBA is estimated for this project
'''
import datetime as dt

class WARCalculator:
    def WRAA(player_df, league_df):
        wOBA = league_df["wOBA"]
        league_wOBA = league_df["league_wOBA"]

        return ((wOBA - league_wOBA) / 1.2) * (player_df["PA"]) #assuming wOBA scale of 1.2

    def BsR(player_df, league_df):
        lgGDP = league_df["GDP"]
        lgGDP_OPP = league_df["GDP_OPP"]
        GDP_OPP = player_df["GDP_OPP"]
        GDP = player_df["GDP"]
        lg_Runs_Per_Out = league_df["RS"] / (league_df["G"] * league_df["INN_per_G"] * 2 * 3) # numer of out = games * innings per game * 2 (teams) * 3 (outs per inning) 
        wGDP = (((lgGDP/lgGDP_OPP) * GDP_OPP)-GDP) * lg_Runs_Per_Out

        SB = player_df["SB"]
        CS = player_df["CS"]
        run_SB = 0.2 #constant
        run_CS = -(2*lg_Runs_Per_Out+0.075)
        lgSB = league_df["SB"]
        lgCS = league_df["CS"]
        lgwSB = ((lgSB*run_SB) + (lgCS*run_CS))/(league_df["1B"] + league_df["BB"] + league_df["HBP"] - league_df["IBB"])
        wSB = (SB * run_SB) + (CS * run_CS) - (lgwSB * (player_df["1B"] + player_df["BB"] + player_df["HBP"] - player_df["IBB"]))

        return wGDP + wSB

    def RPW(player_df, league_df):
        return ((league_df["INN_per_G"]) * (league_df["RS"] / (league_df["G"] * league_df["IP"]*2)) * 1.5) + 3

    def RLR(player_df, league_df):
        return (0.235*league_df["G"]) * RPW(player_df, league_df) * (player_df["PA"]/league_df["PA"]) 

    