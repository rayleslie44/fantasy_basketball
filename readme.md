# Fantasy Basketball League Analysis

## Why I started this project

I started this Python project to develop my own process for collecting, analyzing, and visualizing my Fantasy Basketball league data on ESPN in order to win the 2021-22 championship and exercise my Python and Tableau skills.

This document provides an overview of that process, which ultimately led to me winning the 2021-22 championship. Since then, I have built upon the project with new scripts for the 2022-23 season, which I outline below.

## Connecting to an API

I used this [package](https://github.com/cwendt94/espn-api) that I found on GitHub to connect to ESPN's Fantasy API in order to access and extract my league data.

I wrote Python scripts to pull and prepare the data for analysis:

1. *box_scores.py* was executed during the 2021-22 season and returns a data set of all previous week box scores, up to and including the live box scores of the current week matchups.

2. *box_scores_final.py* was executed at the end of the 2021-22 season and returns a final data set of all box scores.

3. *box.py* is a new and improved script that is executed during the 2022-23 season that returns a final data set of all box scores and W-L-T records. This new script was added after league settings were altered at the start of the new season.

## Scraping a website

4. *player_stats.py* web scrapes Basketball-Reference for [advanced](https://www.basketball-reference.com/leagues/NBA_2022_advanced.html) and [per game](https://www.basketball-reference.com/leagues/NBA_2022_per_game.html) player stats to include in my analysis.

5. *non_matches.py* serves as a fuzzy matching tool that corrects discrepancies in player names between ESPN and Basketball-Reference.

6. *bballreference.py* is a new and improved script that web scrapes Basketball-Reference for any stat type, and also converts the stat type to a z-score.

## Creating rankings

I created a function to convert team box scores and player stats to z-score values. This was a handy way for me to standardize the numbers so that I could create my own measures of who is better than who to monitor during the season.

## Visualizing data

Finally, I created a Tableau dashboard during the 2021-22 season to visualize the data and make decisions about my team during the season. The final dashboard can be viewed [here](https://public.tableau.com/app/profile/ray.leslie/viz/fantasy_basketball/FantasyBasketballLeagueAnalysis).