import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)

import config
import player_stats

rosters_df = config.rosters_df
teams_df = config.teams_df

player_advanced_stats_df = player_stats.player_advanced_stats_df
player_per_game_stats_df = player_stats.player_per_game_stats_df

def non_match_elements(list_a, list_b, list_c):
    non_match = []
    for i in list_a:
        if i not in list_b and list_c:
            non_match.append(i)
    return non_match

list_a = rosters_df['Player'].to_list()
list_b = player_advanced_stats_df['Player'].to_list()
list_c = player_per_game_stats_df['Player'].to_list()

non_match = non_match_elements(list_a, list_b, list_c)

if not non_match:
    print("No non-matches found.")
else: 
    print(non_match)