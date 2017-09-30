#API to return match analytics

from flask import Flask
app = Flask(__name__)


@app.route('/odds')
def match_odds():
    return 'Hello... Odds!'
