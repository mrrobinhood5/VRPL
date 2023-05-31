import requests
from json import dumps
from utils import generate_username, generate_guid, generate_team_name, generate_description, generate_email
from random import randint

api_url = 'http://localhost:8080'

# clear all the collections
drop_db = requests.get(f'{api_url}/db/drop')

# generate 30 players
test_players = [dumps({
    "name": generate_username(),
    "discord_id": generate_guid(),
    "game_uid": generate_guid(),
    "promo_email": generate_email(),
    "calibrated_height": f'{randint(55, 75)} in'}) for x in range(30)]

for player in test_players:
    x = requests.post(f'{api_url}/players/register', data=player)

# get only 5 teams from 5 players
players: dict = requests.get(f'{api_url}/players/all').json()

# make the 5 teams
test_teams = [{
    "name": generate_team_name(),
    "team_motto": generate_description(),
    "captain": player['_id'],
    "team_logo": "https://picsum.photos/200"} for player in players[:5]]

for team in test_teams:
    x = requests.post(f'{api_url}/teams/register', data=dumps(team))

test_teams = requests.get(f'{api_url}/teams/all').json()

# all remaining players request to join teams
remaining_players = [player['_id'] for player in players]

grouped_players = [remaining_players[i:i+5] for i in range(5, len(remaining_players)+1, 5)]
team_ids = [team['_id'] for team in test_teams]


for i, team in enumerate(team_ids):
    for players in grouped_players[i]:
        print({'player': players, 'team': team})
        x = requests.put(f'{api_url}/teams/{team}/join', data=dumps({'player': players}))

# mark all approvals
pending_approvals = requests.get(f'{api_url}/approvals/pending').json()

for approval in pending_approvals:
    x = requests.put(f'{api_url}/teams/approve/{approval["_id"]}', data=dumps({"approved": True}))

# add 5 co_captains
test_teams = requests.get(f'{api_url}/teams/all').json()

for team in test_teams:
    team_players = requests.get(f'{api_url}/teams/{team["_id"]}/players').json()
    x = requests.put(f'{api_url}/teams/{team["_id"]}', data=dumps({'co_captain': team_players[1]['_id']}))
