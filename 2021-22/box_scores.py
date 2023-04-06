# import libraries
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import scipy.stats as stats

# import python file that connects to league using ESPN API
import config

# fetch league info
league = config.league
teams_df = config.teams_df

# fetch all previous week box score data
box_history_df = config.box_history_df

# fetch current week box score data
box = league.box_scores()
score = league.scoreboard()

# create lists for player box score data 
player_name = []
player_box_stats = []
team_name = []
pro_team = []
position = []

# iterate through each matchup
for i in range(len(box)):
    for player in box[i].away_lineup:
        player_name.append(player.name)
        player_box_stats.append(player.points_breakdown)
        team_name.append(box[i].away_team)
        pro_team.append(player.proTeam)
        position.append(player.position)
    for player in box[i].home_lineup:
        player_name.append(player.name)
        player_box_stats.append(player.points_breakdown)
        team_name.append(box[i].home_team)
        pro_team.append(player.proTeam)
        position.append(player.position)

# clean team names
team_name = pd.Series(team_name).astype(str)
new_team_names_list = []
for team in team_name:
    new_team_name = team.replace("Team(", "").replace(")", "")
    new_team_names_list.append(new_team_name)
new_team_names = pd.Series(new_team_names_list).astype(str)

# create data frame for player box score data
box_stats = pd.DataFrame.from_dict(player_box_stats)
box_stats.insert(0, 'Team', new_team_names)
box_stats.insert(1, 'Player', player_name)
box_stats.insert(2, 'Pro Team', pro_team)
box_stats.insert(3, 'Position', position)

# create copy of data frame and drop unused columns
player_box_scores = box_stats.copy()
player_box_scores.drop(['OREB', 'DREB', '', 'PF', 'GS'], axis=1, inplace=True)

# update number formatting for percentage stats
for col in ['FG%', 'FT%', '3PT%']:
    player_box_scores[col] = player_box_scores[col].round(4)
    player_box_scores[col] = player_box_scores[col].apply(lambda x: x * 100).round(4)

player_box_scores['MPG'] = player_box_scores['MPG'].round(1)

# convert all stats to int data type
for col in ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FGM', 'FGA', 'FTM', 'FTA', '3PTM', '3PTA', 'MIN', 'GP']:
    player_box_scores[col] = player_box_scores[col].astype(int)

# fetch team ids and drop team names  
player_box_scores_df = player_box_scores.merge(teams_df)
player_box_scores_df.drop('Team', axis=1, inplace=True)

# reorder columns
player_box_scores_df = player_box_scores_df[
    ['Team ID', 'Player', 'Pro Team', 'Position', 'GP', 'MIN', 'MPG', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 
    '3PTM', '3PTA', '3PT%', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']
    ]

# split data frame by text and stat columns for player z-score analysis
p_txt_cols = player_box_scores_df.iloc[:,0:4]
p_stat_cols = player_box_scores_df.iloc[:,4:]

# convert player box scores to z-scores
player_box_zscores = p_stat_cols.apply(stats.zscore).round(3)

# convert Turnovers to negative values
player_box_zscores['TO'] = player_box_zscores['TO'] * -1

# fill null values with 0
player_box_zscores['GP'] = player_box_zscores['GP'].fillna(0)

# merge text columns back with player z-scores
player_box_zscores_df = player_box_zscores.merge(p_txt_cols, left_index=True, right_index=True)
player_box_zscores_df = player_box_zscores_df[
    ['Team ID', 'Player', 'Pro Team', 'Position', 'GP', 'MIN', 'MPG', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 
    '3PTM', '3PTA', '3PT%', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']
    ]

# drop unused columns
box_stats.drop(['OREB', 'DREB', '', 'PF', '3PTA', 'FG%', 'FT%',
'3PT%', 'MPG', 'MIN', 'GS', 'GP'], axis=1, inplace=True)

# create data frame for team box score data
box_stats_df = box_stats.groupby('Team', as_index=False).sum()

# create column for current week
box_stats_df['Week'] = 23

# calculate percentage stats
box_stats_df['FG%'] = (box_stats_df['FGM'] / box_stats_df['FGA']).round(4)
box_stats_df['FT%'] = (box_stats_df['FTM'] / box_stats_df['FTA']).round(4)

# reoder columns
box_stats_df = box_stats_df[
    ['Week', 'Team', 'FG%', 'FT%', '3PTM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']
    ]

# rename column
box_stats_df.rename({'3PTM': '3PM'}, axis=1, inplace=True)

# convert stats to int data type
for col in ['3PM', 'REB',  'AST', 'STL', 'BLK', 'TO', 'PTS']:
    box_stats_df[col] = box_stats_df[col].astype(int)

# update number formatting for percentage stats
for col in ['FG%', 'FT%']:
    box_stats_df[col] = box_stats_df[col].apply(lambda x: x * 100)

# reorder columns
box_stats_df = box_stats_df[
    ['Week', 'Team', 'FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']
    ]

# create lists for live scoreboard data
team_name_scores = []
scores = []

# iterate through each matchup
for i in range(len(score)):
    team_name_scores.append(score[i].home_team)
    team_name_scores.append(score[i].away_team)
    scores.append(score[i].home_team_live_score)
    scores.append(score[i].away_team_live_score)

# fetch team names and win totals
team_name_scores = pd.Series(team_name_scores).astype(str)
new_team_names_scores_list = []
for team in team_name_scores:
    new_team_name_scores = team.replace("Team(", "").replace(")", "")
    new_team_names_scores_list.append(new_team_name_scores)
new_team_names_scores = pd.Series(new_team_names_scores_list).astype(str)

# convert win totals to series
wins = pd.Series(scores)

# organize live scoreboard data
scores_data = {'Team': new_team_names_scores, 'W': wins}

# create data frame for live scoreboard
scores_df = pd.DataFrame(scores_data)

# calculate loss totals (based on 9 H2H categories)
scores_df['L'] = 9 - scores_df['W']

# convert to int data type
for col in ['W', 'L']:
    scores_df[col] = scores_df[col].astype(int)
    
# calculate tie totals
ties_col = scores_df['W'] + scores_df['L']
scores_df['T'] = [0 if x == 9 else 1 for x in ties_col]

# merge live scoreboard with team box scores
box_stats_scores_df = box_stats_df.merge(scores_df)

# fetch team ids and drop team names
box_current_df = box_stats_scores_df.merge(teams_df)
box_current_df.drop('Team', axis=1, inplace=True)

# reoder columns
box_current_df = box_current_df[
    ['Week', 'Team ID', 'FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']
    ]

# append data frames: current week team box scores to all previous week box scores
box_scores_df = box_history_df.append(box_current_df, ignore_index=True)

# group box score data frame by week for team z-score analysis
box_grouped = box_scores_df.groupby('Week')

# split data frame columns
week_col = box_scores_df.iloc[:,0]
team_id_col = box_scores_df.iloc[:,1]
stat_cols = ['FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']

# convert team box scores to z-scores
box_zscores_df = box_grouped[stat_cols].apply(stats.zscore).round(3)

# convert Turnovers and Losses to negative values
for col in ['TO', 'L']:
    box_zscores_df[col] = box_zscores_df[col] * -1

# convert Ties to count for half a win and fill null values with 0
box_zscores_df['T'] = box_zscores_df['T'] * .5
box_zscores_df['T'] = box_zscores_df['T'].fillna(0)

# add back split columns
box_zscores_df['Week'] = week_col
box_zscores_df['Team ID'] = team_id_col

# reorder columns
box_zscores_df = box_zscores_df[
    ['Week', 'Team ID', 'FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']
    ]

# save all data frames to csv files
box_scores_df.to_csv('box_scores.csv', index=False)
box_zscores_df.to_csv('box_zscores.csv', index=False)
player_box_scores_df.to_csv('player_box_scores.csv', index=False)
player_box_zscores_df.to_csv('player_box_zscores.csv', index=False)