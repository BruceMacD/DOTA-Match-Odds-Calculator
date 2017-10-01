# API to return match analytics

from flask import Flask, jsonify
import math
import json
app = Flask(__name__)


data_folder = 'data/'
data_output_file = 'team-stats.json'


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
