"""
Data analysis tool to predict potential Dota 2 matches
"""

from flask import Flask, jsonify
app = Flask(__name__)
import pandas as pd
import math
import csv
import logging
import json

base_elo = 1600
data_folder = 'data/'
match_details_file = 'match-details.csv'
teams_file = "teams.csv"
id_column = 1
name_column = 0
team_elos = {}
ids_to_names = {}
data_output = {}
data_output_file = 'team-stats.json'


#TODO: Clean up endpoints, make Flask structure
@app.route('/odds/<team_a_id>/<team_b_id>', )
def match_odds(team_a_id, team_b_id):
    probability_a = get_probability_by_id(team_a_id, team_b_id)
    probability_b = 1 - probability_a
    moneyline_a = convert_to_moneyline_odds(probability_a)
    moneyline_b = convert_to_moneyline_odds(probability_b)
    name_a = convert_id_to_team_name(team_a_id)
    name_b = convert_id_to_team_name(team_b_id)

    # create a readable response
    result = {}

    result[team_a_id] = []
    result[team_a_id].append({
        'probability-to-win': str(probability_a),
        'moneyline': str(moneyline_a),
        'team-name' : name_a
    })
    result[team_b_id] = []
    result[team_b_id].append({
        'probability-to-win': str(probability_b),
        'moneyline': str(moneyline_b),
        'team-name' : name_b
    })

    return jsonify(result)


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

        # winner stats, some fields for future use
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


def get_probability_by_id(team_a, team_b):
    # read values from json file serving as mock database
    # team A and B passed by ID
    with open(data_folder + data_output_file) as json_file:
        data = json.load(json_file)
        for p in data[str(team_a)]:
            rating_a = int(p['elo'])
        for p in data[str(team_b)]:
            rating_b = int(p['elo'])

    return probability_a_beats_b(rating_a, rating_b)


def probability_a_beats_b(rating_a, rating_b):
    # method from https://fivethirtyeight.com/features/introducing-nfl-elo-ratings/
    # ELO probability converts to P(A) = 1/(1+10^(m))

    m = (rating_b - rating_a) / 400

    probability_a_wins = 1 / (1 + math.pow(10, m))

    return probability_a_wins


def convert_to_moneyline_odds(prob):
    # convert probability to percent
    percent_chance = prob * 100
    # calculation depends on if probability is above 50% or below
    if percent_chance >= 50:
        odds = - ( percent_chance / (100 - percent_chance)) * 100
    else:
        odds = ((100 - percent_chance) / percent_chance) * 100

    return odds


def convert_id_to_team_name(team_id):
    # read values from json file serving as mock database
    # team A and B passed by ID
    # will set name if match found
    id_name = "none"
    with open(data_folder + data_output_file) as json_file:
        data = json.load(json_file)
        for p in data[str(team_id)]:
            id_name = p['name']

    return id_name


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
            print (i, ids_to_names[i], team_elos[i])
            # add to output json
            id_num = str(i)
            data_output[id_num] = []
            data_output[id_num].append({
                'name': ids_to_names[i],
                'elo': str(team_elos[i])
            })
        except:
            # This is fine, just data from a game against team not in tournament
            logging.info("Team not stored in tournament accessed")

    # save data to file
    with open(data_folder + data_output_file, 'w') as outfile:
        json.dump(data_output, outfile)

