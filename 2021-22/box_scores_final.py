# import libraries
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import scipy.stats as stats

# import python file that connects to league data using ESPN API
import config

# fetch final box scores history data: most recent week and all previous weeks
box_history_df = config.box_history_df

# group box scores data by week
box_grouped = box_history_df.groupby('Week')

# split text and stat columns
week_col = box_history_df.iloc[:,0]
team_id_col = box_history_df.iloc[:,1]
stat_cols = ['FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']

# apply z-score calculation on stats
box_zscores_df = box_grouped[stat_cols].apply(stats.zscore).round(3)

# convert Turnovers and Losses to negative values
for col in ['TO', 'L']:
    box_zscores_df[col] = box_zscores_df[col] * -1

# convert Ties to count for half of a Win
box_zscores_df['T'] = box_zscores_df['T'] * .5

# fill null values with 0
box_zscores_df['T'] = box_zscores_df['T'].fillna(0)

# add back text columns
box_zscores_df['Week'] = week_col
box_zscores_df['Team ID'] = team_id_col

# reorder columns 
box_zscores_df = box_zscores_df[
    ['Week', 'Team ID', 'FG%', 'FT%', '3PM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS', 'W', 'L', 'T']
    ]

# save final box scores history data to csv file
box_history_df.to_csv('box_scores.csv', index=False)

# save final box z-scores history data to csv file
box_zscores_df.to_csv('box_zscores.csv', index=False)