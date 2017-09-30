"""
Data analysis tool to predict potential Dota 2 matches
"""

import pandas as pd
import math
import csv
import logging

base_elo = 1600
data_folder = 'data/'
match_details_file = 'match-details.csv'
teams_file = "teams.csv"
id_column = 1
name_column = 0
team_elos = {}
ids_to_names = {}


def get_elo(team):
    try:
        return team_elos[team]
    except:
        # Set to base elo, team not encountered yet.
        team_elos[team] = base_elo
        return team_elos[team]


def update_elo(w_team_id, l_team_id):
    # current ranks
    winner_elo = get_elo(w_team_id)
    loser_elo = get_elo(l_team_id)

    # Based on how Valve calculates ELO in game
    rank_difference = winner_elo - loser_elo
    experience = (rank_difference * -1) / 400
    odds = 1 / (1 + math.pow(10, experience))
    if winner_elo < 2100:
        points = 32
    elif winner_elo < 2400:
        points = 24
    else:
        points = 16
    new_winner_elo = round(winner_elo + (points * (1 - odds)))
    new_elo_diff = new_winner_elo - winner_elo
    new_loser_elo = loser_elo - new_elo_diff

    team_elos[w_team_id] = new_winner_elo
    team_elos[l_team_id] = new_loser_elo


def analyze_team_stats():
    # using elo to represent overall game performance
    elo = 0
    # read data from matches
    all_data = pd.read_csv(data_folder + match_details_file)

    print("Building season data.")
    # iterate through each row in matches
    for index, row in all_data.iterrows():
        # Used to skip matchups where we don't have usable stats yet.
        skip = 0

        # winner stats
        w_team_id = row['Wteam']
        w_kills = row['Wkills']
        w_deaths = row['Wdeaths']
        w_assists = row['Wassists']
        w_assists = row['Wlast_hits']
        w_denies = row['Wdenies']
        w_xp = row['Wxp_per_min']
        w_gold = row['Wgold_per_min']

        # loser stats
        l_team_id = row['Lteam']
        l_kills = row['Lkills']
        l_deaths = row['Ldeaths']
        l_assists = row['Lassists']
        l_assists = row['Llast_hits']
        l_denies = row['Ldenies']
        l_xp = row['Lxp_per_min']
        l_gold = row['Lgold_per_min']

        # check team
        # w_performance = w_kills - w_deaths + w_assists

        update_elo(w_team_id, l_team_id)


if __name__ == "__main__":

    # store team names to corresponding IDs
    input_names = csv.DictReader(open(data_folder + teams_file))

    #TODO: Fix sometimes reads backwards
    for row in input_names:
        values = list(row.values())

        team_id = int(values[id_column])
        team_name = values[name_column]
        ids_to_names[team_id] = team_name

    analyze_team_stats()

    for i in team_elos:
        try:
            print (ids_to_names[i], team_elos[i])
        except:
            logging.info("Team not stored in tournament accessed")


