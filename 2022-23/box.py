# import libraries
import pandas as pd
from espn import league, teams_df

# define function to get box score data for a given week
def get_box(week):
    
    # get box scores from league
    box = league.box_scores(week)

    # create empty lists to store player box data
    player_name = []
    player_box_stats = []
    team_name = []
    pro_team = []
    position = []

    # loop through each box score matchup
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
    
    # clean and reformat team names
    team_name = pd.Series(team_name).astype(str)
    new_team_names_list = []
    for team in team_name:
        new_team_name = team.replace("Team(", "").replace(")", "")
        new_team_names_list.append(new_team_name)
    new_team_names = pd.Series(new_team_names_list).astype(str)

    # create player box scores dataframe
    box_stats = pd.DataFrame.from_dict(player_box_stats)
    box_stats.insert(0, 'Team', new_team_names)
    box_stats.insert(1, 'Player', player_name)
    box_stats.insert(2, 'Pro Team', pro_team)
    box_stats.insert(3, 'Position', position)
    box_stats.insert(4, 'Week', week)

    # create copy of dataframe and drop column
    player_box_scores = box_stats.copy()
    #player_box_scores = player_box_scores.drop('', axis=1)

    # calculate AFG% column
    player_box_scores['AFG%'] = (player_box_scores['FGM'] + .5 * player_box_scores['3PTM']) / player_box_scores['FGA']
    
    # update number formatting for percentage stats
    for col in ['AFG%', 'FG%', 'FT%', '3PT%']:
        player_box_scores[col] = player_box_scores[col].round(4)
        player_box_scores[col] = player_box_scores[col].apply(lambda x: x * 100).round(4)
    
    player_box_scores['MPG'] = player_box_scores['MPG'].round(1)

    # convert all stats to int data type
    for col in ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FGM', 'FGA', 'FTM', 'FTA', '3PTM', '3PTA', 'MIN', 'GP', 'GS', 'OREB', 'DREB', 'PF']:
        player_box_scores[col] = player_box_scores[col].astype(int)
    
    # get team ids and drop team names  
    player_box_scores_df = player_box_scores.merge(teams_df)
    player_box_scores_df.drop('Team', axis=1, inplace=True)

    # reorder columns
    player_box_scores_df = player_box_scores_df[['Team ID', 'Player', 'Pro Team', 'Position', 'Week', 'GP', 'GS', 'MIN', 'MPG', 'FGM', 'FGA', 'FG%', '3PTM', '3PTA', '3PT%', 'AFG%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF', 'PTS']]

    # return box scores
    return player_box_scores_df

# define function to update current week box score data in box history
def update_box(week):

    # read box history data
    data = pd.read_csv('box_history.csv')
    
    # drop current week box scores from data
    data = data[data['Week']!=week].reset_index(drop=True)

    # get updated box scores for current week
    df = get_box(week)

    # add box scores to main dataframe
    df = df.append(data).reset_index(drop=True)

    # save new box history file
    df.to_csv('box_history.csv', index=False)

# define function to get team record data for a given week
def get_record(week):
    
    # get matchups from league
    matchups = league.scoreboard(week)

    # create empty lists to store team win data
    team_name = []
    wins = []

    # loop through each matchup
    for i in range(len(matchups)):
        team_name.append(matchups[i].home_team)
        team_name.append(matchups[i].away_team)
        wins.append(matchups[i].home_team_live_score)
        wins.append(matchups[i].away_team_live_score)
    
    # clean and reformat team names
    team_name = pd.Series(team_name).astype(str)
    new_team_names_list = []
    for team in team_name:
        new_team_name = team.replace("Team(", "").replace(")", "")
        new_team_names_list.append(new_team_name)
    new_team_names = pd.Series(new_team_names_list).astype(str)

    # create team records dataframe
    box_records = pd.DataFrame()
    box_records.insert(0, 'Team', new_team_names)
    box_records.insert(1, 'Week', week)
    box_records.insert(2, 'Wins', wins)

    # calculate losses (based on 7 H2H categories)
    box_records['Losses'] = 7 - box_records['Wins']

    # convert to ints
    for col in ['Wins', 'Losses']:
        box_records[col] = box_records[col].astype(int)
        
    # calculate ties
    ties_col = box_records['Wins'] + box_records['Losses']
    box_records['Ties'] = [0 if x == 7 else 1 for x in ties_col]

    # get team ids and drop team names
    box_records = box_records.merge(teams_df)
    box_records.drop('Team', axis=1, inplace=True)

    # reorder columns
    box_records = box_records[['Team ID', 'Week', 'Wins', 'Losses', 'Ties']]

    # return team records
    return box_records

# define function to update current week team record data in box records
def update_record(week):

    # read box records data
    data = pd.read_csv('box_records.csv')

    # drop current week team records from data
    data = data[data['Week']!=week].reset_index(drop=True)

    # get updated team records for current week
    df = get_record(week)

    # add team records to main dataframe
    df = df.append(data).reset_index(drop=True)

    # save new box records file
    df.to_csv('box_records.csv', index=False)

# define function to update week box data
def update(week):

    # update box scores and records
    update_box(week)
    update_record(week)
