import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import scipy.stats as stats

import config

box_history_df = config.box_history_df

box_grouped = box_history_df.groupby('Week')

week_col = box_history_df.iloc[:,0]
team_id_col = box_history_df.iloc[:,1]
stat_cols = ['FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']

box_zscores_df = box_grouped[stat_cols].apply(stats.zscore).round(3)

for col in ['TO', 'L']:
    box_zscores_df[col] = box_zscores_df[col] * -1

box_zscores_df['T'] = box_zscores_df['T'] * .5
box_zscores_df['T'] = box_zscores_df['T'].fillna(0)

box_zscores_df['Week'] = week_col
box_zscores_df['Team ID'] = team_id_col

box_zscores_df = box_zscores_df[
    ['Week', 'Team ID', 'FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']
    ]

box_history_df.to_csv('box_scores.csv', index=False)
box_zscores_df.to_csv('box_zscores.csv', index=False)