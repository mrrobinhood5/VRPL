import requests
from json import dumps
from utils import generate_username, generate_guid, generate_team_name, generate_description, generate_email
from random import randint

# clear all the collections
drop_db = requests.get('http://localhost:8080/db/drop')

# generate 30 players
test_players = [dumps({
    "name": generate_username(),
    "discord_id": generate_guid(),
    "game_uid": generate_guid(),
    "promo_email": generate_email(),
    "calibrated_height": f'{randint(55, 75)} in'}) for x in range(30)]

for player in test_players:
    x = requests.post('http://localhost:8080/player/', data=player)

# get only 5 teams from 5 players
team_captains = requests.get('http://localhost:8080/players', params={'n': 5}).json()

# make the 5 teams
test_teams = [dumps({
    "name": generate_team_name(),
    "team_motto": generate_description(),
    "captain": captain['_id']}) for captain in team_captains]

for team in test_teams:
    x = requests.post('http://localhost:8080/team/', data=team)



