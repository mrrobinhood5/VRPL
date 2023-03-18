from fastapi import FastAPI
from testing_utils.build_testing import vrcl, Season, Game, Tournament, Division, Team, Player
from bson.objectid import ObjectId
import uvicorn

app = FastAPI()


@app.get('/')
def read_root():
    """
    This Build Testing version creates
    - **3** Seasons (Only season 2 is populated),
    - **4** Games (Only C$ is populated),
    - **9** Tournament Modes *(only one 1v1)*
    - **2** Divisions *(Randomly populated)*
    - **50** Teams  *(Randomly Generated)*
    - **500** Players *(Randomly Generated)*

    Every restart, all the stats get rebuild from scratch.

    **THIS IS FOR TESTING AND PROOF OF CONCEPT ONLY**
    """
    return vrcl


@app.get('/season/search/{search}')
def season_search(search: str):
    return [season.to_dict for season in Season.get(search)]


@app.get('/seasons')
def all_seasons():
    return [season.to_dict for season in Season.instances()]


@app.get('/season/{season_id}')
def season_by_id(season_id: str):
    return Season.lookup(ObjectId(season_id)).to_dict


@app.get('/season/{season_id}/tournaments')
def season_tournaments(season_id: str):
    return [tournament.to_dict for tournament in Season.lookup(ObjectId(season_id)).tournaments]


@app.get('/games/search/{search}')
def game_search(search: str):
    return [game.to_dict for game in Game.get(search)]


@app.get('/games')
def all_games():
    return [game.to_dict for game in Game.instances()]


@app.get('/game/{game_id}')
def game_by_id(game_id: str):
    return Game.lookup(ObjectId(game_id)).to_dict


@app.get('/tournament/search/{search}')
def tournament_search(search: str):
    return [tournament.to_dict for tournament in Tournament.get(search)]


@app.get('/tournaments')
def all_tournaments():
    return [tournament.to_dict for tournament in Tournament.instances()]


@app.get('/tournament/{tournament_id}')
def tournament_by_id(tournament_id: str):
    return Tournament.lookup(ObjectId(tournament_id)).to_dict


@app.get('/tournament/{tournament_id}/teams')
def tournament_teams(tournament_id: str):
    return [team.to_dict for team in Tournament.lookup(ObjectId(tournament_id)).teams]


@app.get('/divisions')
def all_divisions():
    return [division.to_dict for division in Division.instances()]


@app.get('/division/{division_id}')
def division_by_id(division_id: str):
    return Division.lookup(ObjectId(division_id)).to_dict


@app.get('/division/{division_id}/teams')
def division_teams(division_id: str):
    return [team.to_dict for team in Division.lookup(ObjectId(division_id)).teams]


@app.get('/team/search/{search}')
def team_search(search: str):
    return [team.to_dict for team in Team.get(search)]


@app.get('/teams')
def all_teams():
    return [team.to_dict for team in Team.instances()]


@app.get('/team/{team_id}')
def team_by_id(team_id: str):
    return Team.lookup(ObjectId(team_id)).to_dict


@app.get('/team/{team_id}/players')
def team_players(team_id: str):
    return [player.to_dict for player in Team.lookup(ObjectId(team_id)).players]


@app.get('/player/search/{search}')
def player_search(search: str):
    """
    Search for a players with "search term" in their name.

    This will return a **List[Player]** that matches the "search term"
    """
    return [player.to_dict for player in Player.get(search)]


@app.get('/players')
def all_players():
    return [player.to_dict for player in Player.instances()]


@app.get('/player/{player_id}')
def player_by_id(player_id: str):
    return Player.lookup(ObjectId(player_id)).to_dict


# TODO make the PUT routes


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)
