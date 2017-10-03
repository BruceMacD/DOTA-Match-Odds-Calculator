# eSmarts
Smart predictions for DOTA 2 match results.

Developed for Atlantic Lottery Hackathon 005.

## What is this?

eSmarts is a tool for processing large amounts of Dota 2 match data to determine team rankings. These rankings 
are then used to determine the probability of a given team winning a match.

## Instructions

Use the script in tools/get-matches-from-steam.py to get the required matches from the Steam API. It is required to update 
this tool with your Steam API key before use. I have provided sample match-ids for matches that involved Dota players
that competed in The International 2017. Feel free to update this, I used the OpenDota platform to retrieve this data.

Convert the retrieved match data into a csv file and move it into the data folder. This csv file was too large for github,
feel free to contact me for the match data csv I used.

Install any Python packages you require:
```
sudo pip install pandas
```

and run the application to generate a ranking of the teams:
```
python3 dota2-predictions.py
```

Optionally expose the results with an API for easy access.
```
FLASK_APP=match-odds-controller.py flask run
```

## Future Work
I may expand this to more games and add some more data processing using machine learning techniques. 
