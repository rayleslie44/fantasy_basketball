# import libraries
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)

# import python file that connect to league data using ESPN API
import config

# import python file that contains player stats web scraped from Basketball-Reference.com
import player_stats

# fetch rosters
rosters_df = config.rosters_df

# fetch teams
teams_df = config.teams_df

# create player advanced stats data frame
player_advanced_stats_df = player_stats.player_advanced_stats_df

# create player per game stats data frame
player_per_game_stats_df = player_stats.player_per_game_stats_df

# create function to check for player name mismatches/discrepancies between ESPN and Basketball-Reference.com
def non_match_elements(list_a, list_b, list_c):
    non_match = []
    for i in list_a:
        if i not in list_b and list_c:
            non_match.append(i)
    return non_match

# create list of players from league rosters data frame
list_a = rosters_df['Player'].to_list()

# create list of players from advanced stats data frame
list_b = player_advanced_stats_df['Player'].to_list()

# create list of players from per game stats data frame
list_c = player_per_game_stats_df['Player'].to_list()

# run function to check for player name non-matches
non_match = non_match_elements(list_a, list_b, list_c)

# print player names that do not match if any were found
if not non_match:
    print("No non-matches found.")
else: 
    print(non_match)