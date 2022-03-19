import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)

import scipy.stats as stats
from numpy import std
from numpy import mean

import config
rosters_df = config.rosters_df

import requests
from bs4 import BeautifulSoup

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
    
    df = pd.DataFrame(players_br, columns=column_names_clean)
    
    df['Player'] = df['Player'].str.replace('*','', regex=True)
    df['Player'] = df['Player'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df['Player'] = df['Player'].replace(
        ['Marcus Morris',  'Robert Williams'], 
        ['Marcus Morris Sr.', 'Robert Williams III'])
    
    df_col_drop = ['Pos', 'Age', 'Tm']
    df.drop(df_col_drop, axis=1, inplace=True)

    df = df.replace('', 0)
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(float)

    if x == 'advanced':
        df = df[
            ['Player','G','MP','PER','TS%','3PAr','FTr','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%',
            'USG%','OWS','DWS','WS','WS/48','OBPM','DBPM','BPM','VORP']
            ]

        df['WORP'] = (df['VORP'] * 2.7).round(1)
        df = df.fillna(0)

        for col in ['TS%', '3PAr', 'FTr', 'WS/48']:
            df[col] = df[col].apply(lambda x: x * 100)
        
        advanced_df = rosters_df.merge(df, how='left')
        advanced_df = advanced_df.fillna(0)
        
        return advanced_df

    elif x == 'per_game':
        df = df[
            ['Player','G','GS','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%','eFG%','FT',
            'FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS']
            ]

        ast_to_ratio = (df['AST'] / df['TOV']).round(1)
        df['AST/TOV'] = ast_to_ratio

        df = df.fillna(0)
        for col in ['FG%', '3P%', '2P%', 'eFG%', 'FT%']:
            df[col] = df[col].apply(lambda x: x * 100)
        
        per_game_df = rosters_df.merge(df, how='left')
        per_game_df = per_game_df.fillna(0)
        
        return per_game_df

def player_zstats(x):
    txt_cols = x.iloc[:,:5]
    stat_cols = x.iloc[:,5:]

    stat_cols_std = std(stat_cols['MP'])
    stat_cols_avg = mean(stat_cols['MP'])

    lower_cutoff = stat_cols_avg - stat_cols_std
    stat_cols = stat_cols[stat_cols['MP'] >= lower_cutoff]

    stat_cols = stat_cols.apply(stats.zscore).round(3)

    if x.shape[1] == 28: # advanced

        stat_cols['TOV%'] = stat_cols['TOV%'] * -1

        advanced_z = stat_cols.merge(txt_cols, left_index=True, right_index=True)
        advanced_z = advanced_z[
            ['Team ID', 'Player', 'Pro Team', 'Position', 'Injury Status', 'G', 'MP', 'PER', 'TS%', '3PAr', 
            'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/48', 
            'OBPM', 'DBPM', 'BPM', 'VORP', 'WORP']
            ]
        
        return advanced_z
    
    elif x.shape[1] == 31: # per_game

        stat_cols['TOV'] = stat_cols['TOV'] * -1

        per_game_z = stat_cols.merge(txt_cols, left_index=True, right_index=True)
        per_game_z = per_game_z[
            ['Team ID', 'Player', 'Pro Team', 'Position', 'Injury Status', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', 
            '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 
            'BLK', 'TOV', 'PF', 'PTS', 'AST/TOV']
            ]
        
        return per_game_z

player_advanced_stats_df = player_stats('advanced')
player_per_game_stats_df = player_stats('per_game')

player_advanced_zstats_df = player_zstats(player_advanced_stats_df)
player_per_game_zstats_df = player_zstats(player_per_game_stats_df)

player_advanced_stats_df.to_csv('player_advanced_stats.csv', index=False)
player_per_game_stats_df.to_csv('player_per_game_stats.csv', index=False)

player_advanced_zstats_df.to_csv('player_advanced_zstats.csv', index=False)
player_per_game_zstats_df.to_csv('player_per_game_zstats.csv', index=False)