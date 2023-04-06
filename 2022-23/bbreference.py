# import libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
import scipy.stats as stats
from numpy import std
from numpy import mean

# define function to scrape basketball-reference.com for player stats
def get_player_stats(year,stat_type):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_{stat_type}.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all(class_='full_table')
    head = soup.find(class_='thead')
    
    # grab columns and apply formatting
    column_names_raw = [head.text for item in head][0]
    column_names_clean = column_names_raw.replace('\n',',').split(',')[2:-1]
    
    # find all players in table
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
    df['Player'] = df['Player'].replace(['Marcus Morris',  'Robert Williams'], ['Marcus Morris Sr.', 'Robert Williams III'])

    # replace blanks with 0 and convert columns to float
    df = df.replace('', 0)
    df.iloc[:, 4:] = df.iloc[:, 4:].astype(float)

    # update position column
    df['Pos'] = df['Pos'].replace(['SF-SG', 'SG-PG', 'SG-SF', 'SF-PF', 'PG-SG', 'C-PF', 'PF-C', 'PF-SF', 'SG-PG-SF', 'SF-C', 'SG-PF'], ['SF', 'SG', 'SG', 'SF', 'PG', 'C', 'PF', 'PF', 'SG', 'SF', 'SG'])

    # return data frame
    return df

# define function to convert data frame from player stats to z-scores
def get_player_zscores(year,stat_type):
    
    # define data frame
    df = get_player_stats(year, stat_type)
    
    # create year column
    df['Year'] = year

    # if stat type equals totals, grab certain columns
    if stat_type == 'totals':
    
        # create copy of data frame using certain columns
        dfc = df[['Year', 'Player', 'Pos', 'Tm', 'MP', 'eFG%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'PTS']].copy()
    
    # if stat type equals advanced, grab certain columns
    elif stat_type == 'advanced':

        dfc = df[['Year', 'Player', 'Pos', 'Tm', 'MP', 'PER', 'TS%', 'USG%', 'WS', 'VORP']].copy()
    
    # split text and stat columns
    text_cols = dfc.iloc[:,:4]
    stat_cols = dfc.iloc[:,4:]
    
    # calculate standard deviation and average Minutes Played of all players
    stat_cols_std = std(stat_cols['MP'])
    stat_cols_avg = mean(stat_cols['MP'])
    
    # calculate minimum Minutes Played to account for players who did not play enough minutes
    lower_cutoff = stat_cols_avg - stat_cols_std
    
    # filter out players who did not meet minimum Minutes Played requirement
    stat_cols = stat_cols[stat_cols['MP'] >= lower_cutoff]

    # if stat type equals totals, drop column then apply zscore
    if stat_type == 'totals':
        
        # drop column
        stat_cols = stat_cols.drop('MP', axis=1)
    
    # apply z-score calculation to stat columns
    stat_cols = stat_cols.apply(stats.zscore).round(2)

    # sum scoring stats to get overall score
    stat_cols['zScore'] = stat_cols.sum(axis=1)

    # create overall rank column based on scoring stats
    stat_cols['zRank'] = stat_cols['zScore'].rank(ascending=False).astype(int).round(0)

    # merge back text and stat columns
    dfz = text_cols.merge(stat_cols, left_index=True, right_index=True)

    # create position rank column based on overall score
    dfz['pRank'] = dfz.groupby('Pos')['zScore'].rank(ascending=False).astype(int).round(0)

    # sort by overall rank column and reset index
    dfz = dfz.sort_values(by='zRank', ascending=True).reset_index(drop=True)
    
    # return player z-scores data frame
    return dfz
