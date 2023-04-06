# import libraries
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)

import scipy.stats as stats
from numpy import std
from numpy import mean

# import rosters from python file that connects to ESPN API
import config
rosters_df = config.rosters_df

import requests
from bs4 import BeautifulSoup

# create function to web scrape player stats from Basketball-Reference.com
def player_stats(x):
    url = 'https://www.basketball-reference.com/leagues/NBA_2022_{0}.html'.format(x)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all(class_='full_table')
    head = soup.find(class_='thead')
    column_names_raw = [head.text for item in head][0]
    column_names_clean = column_names_raw.replace('\n',',').split(',')[2:-1]
    players_br = []
    for i in range(len(table)):
        player_ = []
        for td in table[i].find_all('td'):
            player_.append(td.text)
        players_br.append(player_)
    # create data frame from web scraped data
    df = pd.DataFrame(players_br, columns=column_names_clean)
    # normalize player names to match ESPN    
    df['Player'] = df['Player'].str.replace('*','', regex=True)
    df['Player'] = df['Player'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df['Player'] = df['Player'].replace(
        ['Marcus Morris',  'Robert Williams'], 
        ['Marcus Morris Sr.', 'Robert Williams III'])
    # drop unused columns     
    df_col_drop = ['Pos', 'Age', 'Tm']
    df.drop(df_col_drop, axis=1, inplace=True)
    # replace blanks with 0
    df = df.replace('', 0)
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(float)
    # web scrape player advanced stats
    if x == 'advanced':
        df = df[
            ['Player','G','MP','PER','TS%','3PAr','FTr','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%',
            'USG%','OWS','DWS','WS','WS/48','OBPM','DBPM','BPM','VORP']
            ]
        # calculate Value over Replacement Player metric
        df['WORP'] = (df['VORP'] * 2.7).round(1)
        df = df.fillna(0)
        # update number formatting for percentage stats
        for col in ['TS%', '3PAr', 'FTr', 'WS/48']:
            df[col] = df[col].apply(lambda x: x * 100)
        # merge data frames: player advanced stats with rosters
        advanced_df = rosters_df.merge(df, how='left')
        # fill null values with 0: for players who did not play or generate enough stats
        advanced_df = advanced_df.fillna(0)
        # return player advanced stats data frame
        return advanced_df
    # web scrape player per game stats
    elif x == 'per_game':
        # create data frame from web scraped data
        df = df[
            ['Player','G','GS','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%','eFG%','FT',
            'FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS']
            ]
        # calculate Assist to Turnover ratio metric
        ast_to_ratio = (df['AST'] / df['TOV']).round(1)
        df['AST/TOV'] = ast_to_ratio
        # replace blanks with 0
        df = df.fillna(0)
        # update number formatting for percentage stats
        for col in ['FG%', '3P%', '2P%', 'eFG%', 'FT%']:
            df[col] = df[col].apply(lambda x: x * 100)
        # merge data frames: player per game stats with rosters
        per_game_df = rosters_df.merge(df, how='left')
        # fill null values with 0: for players who did not play or generate enough stats
        per_game_df = per_game_df.fillna(0)
        # return player per game stats data frame
        return per_game_df

# create function to convert web scraped player stats data to z-scores
def player_zstats(x):
    # split text and stat columns
    txt_cols = x.iloc[:,:5]
    stat_cols = x.iloc[:,5:]
    # calculate standard deviation and average Minutes Played of all players
    stat_cols_std = std(stat_cols['MP'])
    stat_cols_avg = mean(stat_cols['MP'])
    # calculate minimum Minutes Played to account for players who did not play enough minutes
    lower_cutoff = stat_cols_avg - stat_cols_std
    # filter out players who did not meet minimum Minutes Played requirement
    stat_cols = stat_cols[stat_cols['MP'] >= lower_cutoff]
    # apply z-score calculation to stat columns
    stat_cols = stat_cols.apply(stats.zscore).round(3)

    # calculate z-scores for player advanced stats data frame
    if x.shape[1] == 28:
        # convert Turnovers to negative values
        stat_cols['TOV%'] = stat_cols['TOV%'] * -1
        # merge back with text columns
        advanced_z = stat_cols.merge(txt_cols, left_index=True, right_index=True)
        # reorder columns
        advanced_z = advanced_z[
            ['Team ID', 'Player', 'Pro Team', 'Position', 'Injury Status', 'G', 'MP', 'PER', 'TS%', '3PAr', 
            'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/48', 
            'OBPM', 'DBPM', 'BPM', 'VORP', 'WORP']
            ]
        # return player advanced z-score stats data frame
        return advanced_z
    
    # calculate z-scores for player per game stats data frame
    elif x.shape[1] == 31:
        # convert Turnovers to negative values
        stat_cols['TOV'] = stat_cols['TOV'] * -1
        # merge back with text columns
        per_game_z = stat_cols.merge(txt_cols, left_index=True, right_index=True)
        # reorder columns
        per_game_z = per_game_z[
            ['Team ID', 'Player', 'Pro Team', 'Position', 'Injury Status', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', 
            '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 
            'BLK', 'TOV', 'PF', 'PTS', 'AST/TOV']
            ]
        # return player per game z-score stats data frame
        return per_game_z

# create player advanced and per game stats data frames
player_advanced_stats_df = player_stats('advanced')
player_per_game_stats_df = player_stats('per_game')

# create player advanced and per game z-score stats data frames
player_advanced_zstats_df = player_zstats(player_advanced_stats_df)
player_per_game_zstats_df = player_zstats(player_per_game_stats_df)

# save player advanced and per game stats data frames to csv files
player_advanced_stats_df.to_csv('player_advanced_stats.csv', index=False)
player_per_game_stats_df.to_csv('player_per_game_stats.csv', index=False)

# save player advanced and per game z-score stats data frames to csv files
player_advanced_zstats_df.to_csv('player_advanced_zstats.csv', index=False)
player_per_game_zstats_df.to_csv('player_per_game_zstats.csv', index=False)