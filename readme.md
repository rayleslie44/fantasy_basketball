# Fantasy Basketball League Analysis

## Why I started this project

I started this Python project to develop my own process for collecting, analyzing, and visualizing my Fantasy Basketball league data on ESPN in order to win the championship and exercise my Python and Tableau skills.

This document provides an overview of that process, which ultimately led to me winning the championship.

## Connecting to an API

I used this [package](https://github.com/cwendt94/espn-api) that I found on GitHub to connect to ESPN's Fantasy API in order to access and extract my league data.

I wrote four Python scripts to pull and prepare the data for analysis:

1. *box_scores.py* is executed during the season and returns a data set of all previous week box scores, up to and including the live box scores of the current week matchups.

2. *box_scores_final.py* is executed at the end of the season and returns a final data set of all box scores.

## Scraping a website

3. *player_stats.py* web scrapes Basketball-Reference for [advanced](https://www.basketball-reference.com/leagues/NBA_2022_advanced.html) and [per game](https://www.basketball-reference.com/leagues/NBA_2022_per_game.html) player stats to include in my analysis.

4. *non_matches.py* serves as a fuzzy matching tool that corrects discrepancies in player names between ESPN and Basketball-Reference.

## Creating rankings

In addition, I created a function in each script to convert team box scores and player stats to z-score values, which use a statistical measure of the distance from the mean.

This type of data was useful to include in my analysis because it allowed me to create my own measures of who is better than who, rather than solely relying on standard stats.

## Visualizing data

Finally, I created a Tableau dashboard to visualize the data and make decisions about my team during the season. The final dashboard can be viewed here.