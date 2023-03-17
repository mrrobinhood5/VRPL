from fastapi import FastAPI
from testing_utils import build_testing
from testing_utils.build_testing import vrcl, Season, Game, Tournament,Division, Team, Player
from bson.objectid import ObjectId
import uvicorn

app = FastAPI()


@app.get('/')
def read_root():
    return vrcl


@app.get('/seasons')
def seasons():
    return [season.to_dict for season in Season.instances()]


@app.get('/season/{season_id}')
def season_lookup(season_id: str):
    return Season.lookup(ObjectId(season_id)).to_dict

@app.get('/season/search/{search}')
def season_search(search: str):
    return [season.to_dict for season in Season.get(search)]


@app.get('/season/{season_id}/tournaments')
def season_tournaments(season_id: str):
    return [tournament.to_dict for tournament in Season.lookup(ObjectId(season_id)).tournaments]

@app.get('/games')
def games():
    return [game.to_dict for game in Game.instances()]

@app.get('/games/search/{search}')
def game_search(search: str):
    return [game.to_dict for game in Game.get(search)]

@app.get('/game/{game_id}')
def games(game_id: str):
    return Game.lookup(ObjectId(game_id)).to_dict

@app.get('/tournaments')
def tournaments():
    return [tournament.to_dict for tournament in Tournament.instances()]

@app.get('/tournament/search/{search}')
def tournament_search(search: str):
    return [tournament.to_dict for tournament in Tournament.get(search)]

@app.get('/tournament/{tournament_id}')
def tournament(tournament_id: str):
    return Tournament.lookup(ObjectId(tournament_id)).to_dict

@app.get('/tournament/{tournament_id}/teams')
def tournament_teams(tournament_id:str):
    return [team.to_dict for team in Tournament.lookup(ObjectId(tournament_id)).teams]

@app.get('/divisions')
def divisions():
    return [division.to_dict for division in Division.instances()]

@app.get('/division/{division_id}')
def division(division_id: str):
    return Division.lookup(ObjectId(division_id)).to_dict

@app.get('/teams')
def teams():
    return [team.to_dict for team in Team.instances()]

@app.get('/team/search/{search}')
def team_search(search: str):
    return [team.to_dict for team in Team.get(search)]

@app.get('/team/{team_id}')
def team(team_id: str):
    return Team.lookup(ObjectId(team_id)).to_dict

@app.get('/team/{team_id}/players')
def team_players(team_id: str):
    return [player.to_dict for player in Team.lookup(ObjectId(team_id)).players]

@app.get('/players')
def players():
    return [player.to_dict for player in Player.instances()]

@app.get('/player/search/{search}')
def player(search: str):
    return [player.to_dict for player in Player.get(search)]

@app.get('/player/{player_id}')
def player(player_id: str):
    return Player.lookup(ObjectId(player_id)).to_dict

# TODO make the PUT routes

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)