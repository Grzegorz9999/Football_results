import numpy as np
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('soccerData.csv')
df['date_GMT']= pd.to_datetime(df['date_GMT'])

raw_match_stats = df[[
 'date_GMT',
 'home_team_name',
 'away_team_name',
 'home_team_goal_count',
 'away_team_goal_count',
 'home_team_corner_count',
 'away_team_corner_count',
 'home_team_shots',
 'away_team_shots',
 'home_team_shots_on_target',
 'away_team_shots_on_target',
 'home_team_fouls',
 'away_team_fouls',
 'home_team_possession',
 'away_team_possession',]]

raw_match_stats = raw_match_stats.sort_values(by=['date_GMT'], ascending=False)
raw_match_stats = raw_match_stats.dropna()

print(raw_match_stats)

# create results columns for both home and away teams (W - win, D = Draw, L = Loss).

raw_match_stats.loc[raw_match_stats['home_team_goal_count'] == raw_match_stats['away_team_goal_count'], 'home_team_result'] = 'D'
raw_match_stats.loc[raw_match_stats['home_team_goal_count'] > raw_match_stats['away_team_goal_count'], 'home_team_result'] = 'W'
raw_match_stats.loc[raw_match_stats['home_team_goal_count'] < raw_match_stats['away_team_goal_count'], 'home_team_result'] = 'L'

raw_match_stats.loc[raw_match_stats['home_team_goal_count'] == raw_match_stats['away_team_goal_count'], 'away_team_result'] = 'D'
raw_match_stats.loc[raw_match_stats['home_team_goal_count'] > raw_match_stats['away_team_goal_count'], 'away_team_result'] = 'L'
raw_match_stats.loc[raw_match_stats['home_team_goal_count'] < raw_match_stats['away_team_goal_count'], 'away_team_result'] = 'W'

# Split the raw_match_stats to two datasets (home_team_stats and away_team_stats)

home_team_stats = raw_match_stats[[
 'date_GMT',
 'home_team_name',
 'home_team_goal_count',
 'home_team_corner_count',
 'home_team_shots',
 'home_team_shots_on_target',
 'home_team_fouls',
 'home_team_possession',
 'home_team_result',]]

away_team_stats = raw_match_stats[[
 'date_GMT',
 'away_team_name',
 'away_team_goal_count',
 'away_team_corner_count',
 'away_team_shots',
 'away_team_shots_on_target',
 'away_team_fouls',
 'away_team_possession',
 'away_team_result',]]

# rename "home_team" and "away_team" columns
home_team_stats.columns = [col.replace('home_team_','') for col in home_team_stats.columns]
away_team_stats.columns = [col.replace('away_team_','') for col in away_team_stats.columns]

# stack these two datasets so that each row is the stats for a team for one match (team_stats_per_match)
team_stats_per_match = home_team_stats.append(away_team_stats)
# Split the raw_match_stats to two datasets (home_team_stats and away_team_stats)

home_team_stats = raw_match_stats[[
 'date_GMT',
 'home_team_name',
 'home_team_goal_count',
 'home_team_corner_count',
 'home_team_shots',
 'home_team_shots_on_target',
 'home_team_fouls',
 'home_team_possession',
 'home_team_result',]]

away_team_stats = raw_match_stats[[
 'date_GMT',
 'away_team_name',
 'away_team_goal_count',
 'away_team_corner_count',
 'away_team_shots',
 'away_team_shots_on_target',
 'away_team_fouls',
 'away_team_possession',
 'away_team_result',]]

# rename "home_team" and "away_team" columns
home_team_stats.columns = [col.replace('home_team_','') for col in home_team_stats.columns]
away_team_stats.columns = [col.replace('away_team_','') for col in away_team_stats.columns]

# stack these two datasets so that each row is the stats for a team for one match (team_stats_per_match)
team_stats_per_match = home_team_stats.append(away_team_stats)

# At each row of this dataset, get the team name, find the stats for that team during the last 5 matches, and average these stats (avg_stats_per_team).

avg_stat_columns = ['goals_per_match','corners_per_match','shots_per_match','shotsOnTarget_per_match','fouls_per_match', 'possession_per_match']
stats_list = []
for index, row in team_stats_per_match.iterrows():
    team_stats_last_five_matches = team_stats_per_match.loc[(team_stats_per_match['name']==row['name']) & (team_stats_per_match['date_GMT']<row['date_GMT'])].sort_values(by=['date_GMT'], ascending=False)
    stats_list.append(team_stats_last_five_matches.iloc[0:5,:].mean(axis=0).values[0:6])

avg_stats_per_team = pd.DataFrame(stats_list, columns=avg_stat_columns)

# Add these stats to the team_stats_per_match dataset.

team_stats_per_match = pd.concat([team_stats_per_match.reset_index(drop=True), avg_stats_per_team], axis=1, ignore_index=False)

# Re-segment the home and away teams.

home_team_stats = team_stats_per_match.iloc[:int(team_stats_per_match.shape[0]/2),:]
away_team_stats = team_stats_per_match.iloc[int(team_stats_per_match.shape[0]/2):,:]

home_team_stats.columns = ['team_1_'+str(col) for col in home_team_stats.columns]
away_team_stats.columns = ['team_2_'+str(col) for col in away_team_stats.columns]

# Combine at each match to get a dataset with a row representing each match.
# drop the NA rows (earliest match for each team, i.e no previous stats)

match_stats = pd.concat([home_team_stats, away_team_stats.reset_index(drop=True)], axis=1, ignore_index=False)
match_stats = match_stats.dropna().reset_index(drop=True)

# create columns with average stat differences between the two teams

match_stats['goals_per_match_diff'] = (match_stats['team_1_goals_per_match'] - match_stats['team_2_goals_per_match'])
match_stats['corners_per_match_diff'] = (match_stats['team_1_corners_per_match'] - match_stats['team_2_corners_per_match'])
match_stats['shots_per_match_diff'] = (match_stats['team_1_shots_per_match'] - match_stats['team_2_shots_per_match'])
match_stats['shotsOnTarget_per_match_diff'] = (match_stats['team_1_shotsOnTarget_per_match'] - match_stats['team_2_shotsOnTarget_per_match'])
match_stats['fouls_per_match_diff'] = (match_stats['team_1_fouls_per_match'] - match_stats['team_2_fouls_per_match'])
match_stats['possession_per_match_diff'] = (match_stats['team_1_possession_per_match'] - match_stats['team_2_possession_per_match'])

print(match_stats)