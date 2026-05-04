from cleaner import load_player_stats, load_league_stats
from Pipeline import WRAA, BsR, RLR, RPW
import pandas as pd

def main():

    league_stats = load_league_stats()
    all_players = league_stats[['Name', 'Age']].drop_duplicates()
    data_rows = []

    #calculate for all p[layer so we can build ML dataset, since the year is from 2021-2025 we need to go through a lot of player 
    for _, row in all_players.iterrows():
            player_name = row['Name']
            age = row['Age']
            player_stats = load_player_stats(player_name)

            wraa = WRAA(player_stats, league_stats)
            bsr = BsR(player_stats, league_stats)
            rlr = RLR(player_stats, league_stats)
            rpw = RPW(player_stats, league_stats)

            owar = (wraa + bsr + rlr) / rpw

            age = player_stats['Age'].values[0]  
            data_rows.append({'Name': player_name, 'Age': age, 'oWAR': owar})
    ml_set = pd.DataFrame(data_rows)
    ml_set.to_csv("age_vs_owar.csv", index=False)

'''
Many assumptions were made in this project such as
assuming full 162 game season for all teams
asuming 9 inning game, disregarding extra inning or called off games
Also defensive WAR were omitted which may cause up to 2WAR difference per player
'''
if __name__ == "__main__":
    main()