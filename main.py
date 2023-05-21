from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from classes.players import PlayerModel, UpdatePlayerModel, PlayerTeamModel, UpdatePlayerTeamModel
from classes.teams import TeamModel, UpdateTeamModel
from typing import List

from database import db_add_one, db_find_all, db_find_one, db_update_one, db_find_some
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
    return {"Testing": "ok"}


# @app.get('/season/search/{search}')
# def season_search(search: str):
#     return [season.to_dict for season in Season.get(search)]
#
#
# @app.get('/seasons')
# def all_seasons():
#     return [season.to_dict for season in Season.instances()]
#
#
# @app.get('/season/{season_id}')
# def season_by_id(season_id: str):
#     return Season.lookup(ObjectId(season_id)).to_dict
#
#
# @app.get('/season/{season_id}/tournaments')
# def season_tournaments(season_id: str):
#     return [tournament.to_dict for tournament in Season.lookup(ObjectId(season_id)).tournaments]
#
#
# @app.get('/games/search/{search}')
# def game_search(search: str):
#     return [game.to_dict for game in Game.get(search)]
#
#
# @app.get('/games')
# def all_games():
#     return [game.to_dict for game in Game.instances()]
#
#
# @app.get('/game/{game_id}')
# def game_by_id(game_id: str):
#     return Game.lookup(ObjectId(game_id)).to_dict
#
#
# @app.get('/tournament/search/{search}')
# def tournament_search(search: str):
#     return [tournament.to_dict for tournament in Tournament.get(search)]
#
#
# @app.get('/tournaments')
# def all_tournaments():
#     return [tournament.to_dict for tournament in Tournament.instances()]
#
#
# @app.get('/tournament/{tournament_id}')
# def tournament_by_id(tournament_id: str):
#     return Tournament.lookup(ObjectId(tournament_id)).to_dict
#
#
# @app.get('/tournament/{tournament_id}/teams')
# def tournament_teams(tournament_id: str):
#     return [team.to_dict for team in Tournament.lookup(ObjectId(tournament_id)).teams]
#
#
# @app.get('/divisions')
# def all_divisions():
#     return [division.to_dict for division in Division.instances()]
#
#
# @app.get('/division/{division_id}')
# def division_by_id(division_id: str):
#     return Division.lookup(ObjectId(division_id)).to_dict
#
#
# @app.get('/division/{division_id}/teams')
# def division_teams(division_id: str):
#     return [team.to_dict for team in Division.lookup(ObjectId(division_id)).teams]

#
# @app.get('/team/search/{search}')
# def team_search(search: str):
#     return [team.to_dict for team in Team.get(search)]
#
#
# @app.get('/teams')
# def all_teams():
#     return [team.to_dict for team in Team.instances()]
#
#
# @app.get('/team/{team_id}')
# def team_by_id(team_id: str):
#     return Team.lookup(PydanticObjectId(team_id)).to_dict
#
#
# @app.get('/team/{team_id}/players')
# def team_players(team_id: str):
#     return [player.to_dict for player in Team.lookup(PydanticObjectId(team_id)).players]
#

# @app.get('/player/search/{search}')
# def player_search(search: str):
#     """
#     Search for a players with "search term" in their name.
#
#     This will return a **List[Player]** that matches the "search term"
#     """
#     return [player.to_dict for player in Player.get(search)]
#
#
# @app.get('/players')
# def all_players():
#     return [player.to_dict for player in Player.instances()]
#
#
# @app.get('/player/{player_id}')
# def player_by_id(player_id: str):
#     return Player.lookup(PydanticObjectId(player_id)).to_dict


# @app.post('/player/')
# def create_player(player: Player):
#     Player(player)
#     return "ok"

@app.post("/player/", response_description="Register a new Player", response_model=PlayerModel)
async def register_player(player: PlayerModel = Body(...)):
    """ To register a Player, you only need to send in
    ```"name" : "Chosen Name to be used in-game",
    "discord_id": "DISCORD_ID from the discord API",
    "game_uid": "uid from c$",
    "height": "5ft 6in"``` """
    # TODO: Check to see if the discord_id already exists
    created_player = await db_add_one(player, "players")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@app.get("/players", response_description="List all registered players", response_model=List[PlayerModel])
async def list_players():
    """ Lists all registered players from the DB """
    players = await db_find_all("players", 1000)
    return players


@app.get("/player/{id}", response_description="Get a single player", response_model=PlayerModel)
async def show_player(id: str):
    """ To retrieve a single player, send in just the ObjectID for the player """
    # TODO: maybe also take in a discord_id
    if player := await db_find_one(id, "players") is not None:
        return player
    raise HTTPException(status_code=404, detail=f"Player {id} not found")


@app.put("/player/{id}", response_description="Update a player", response_model=PlayerModel)
async def update_player(id: str, player: UpdatePlayerModel = Body(...)):
    """ Updatable fields are:
    ```"name": "If you are planning on changing the in-game name",
    "email": "to make email updates",
    "game_uid": "to make corrections to the UID",
    "height": "to make corrections to the in-game height",
    "belongs_to_team": ["list of Team ObjectIDs"],
    "belongs_to_tournament": ["list of Tournament ObjectID"]. Primarily 1V1 tournaments```
    """
    player = {k: v for k, v in player.dict().items() if v is not None}
    if len(player) >= 1:
        update_result = await db_update_one(id, 'players', player)
        if update_result.modified_count == 1:
            if (
                    updated_player := await db_find_one(id, 'players')
            ) is not None:
                return updated_player
    if existing_player := await db_find_one(id, 'players') is not None:
        return existing_player
    raise HTTPException(status_code=404, detail=f"Player {id} not found")


@app.post("/team/", response_description="Register a new Team", response_model=TeamModel)
async def register_team(team: TeamModel = Body(...)):
    """ To register a team you need to send in:
    ```"name": "Official Team Name",
    "captain": "The captains Player ObjectID",
    "team_motto": "A brief Motto"```
    """
    # TODO: Team Captain needs to be added to the team
    created_team = await db_add_one(team, 'teams')
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_team)


@app.get("/teams", response_description="List all registered teams", response_model=List[TeamModel])
async def list_teams():
    """ Lists all registered teams """
    teams = await db_find_all('teams', 100)
    return teams


@app.get("/team/{id}", response_description="Get a single Team", response_model=TeamModel)
async def show_team(id: str):
    """ To retrieve a specific team, provide the Team ObjectID """
    if team := await db_find_one(id, 'teams') is not None:
        return team
    raise HTTPException(status_code=404, detail=f"Team {id} not found")


@app.put("/team/{id}", response_description="Update a team", response_model=TeamModel)
async def update_team(id: str, team: UpdateTeamModel = Body(...)):
    """ The following team fields can be updated:
     ```"name" : "Updated team name",
     "team_motto": "Updated team motto",
     "captain": "provide 1 Player ObjectID for new captain",
     "team_logo": "url for a team logo image",
     "co_captain": "player ObjectID for a co-captain. They can also make changes to the team",
     "belongs_to_division": ["Division ObjectID"],
     "belongs_to_tournaments": ["Tournament ObjectID"],
     "active": False or True to mark as active``` """
    team = {k: v for k, v in team.dict().items() if v is not None}
    if len(team) >= 1:
        update_result = await db_update_one(id, 'teams', team)
        if update_result.modified_count == 1:
            if (
                    updated_team := await db_find_one(id, 'team')
            ) is not None:
                return updated_team
    if existing_team := await db_find_one(id, 'teams') is not None:
        return existing_team
    raise HTTPException(status_code=404, detail=f"Team {id} not found")


@app.get("/team/{id}/approvals", response_description="List all pending Approvals", response_model=List[PlayerTeamModel])
async def list_pending_approvals(id: str):
    # results = await db_find_some("player_team_link", {"team": {"$eq": id}, "approved": {"$ne": True}})
    results = await db_find_some("player_team_link", {"team": id, "approved": None})
    return results


@app.get("/team/{id}/players", response_description="List all Players in a Team", response_model=List[PlayerModel])
async def list_team_players(id: str):
    results = await db_find_some("players", {"team": id, "approved": True})
    return results #TODO this is where I left off


@app.put("/team/join/", response_description="Request to Join a Team", response_model=PlayerTeamModel)
async def request_to_join_team(request: PlayerTeamModel = Body(...)):
    """ To request to join a team, a player creates a request
     and a team has to approve it """
    created_player = await db_add_one(request, "player_team_link")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@app.put("/team/approve/{id}", response_description="Approve a team join", response_model=PlayerTeamModel)
async def approve_team_join(id: str, request: UpdatePlayerTeamModel = Body(...)):
    """ Approve or Decline a team join """
    request = {k: v for k, v in request.dict().items() if v is not None}
    if len(request) >= 1:
        update_result = await db_update_one(id, 'player_team_link', request)
        if update_result.modified_count == 1:
            if (
                    updated_request := await db_find_one(id, 'player_team_link')
            ) is not None:
                return updated_request
    if existing_request := await db_find_one(id, 'player_team_link') is not None:
        return existing_request
    raise HTTPException(status_code=404, detail=f"Team Join request {id} not found")

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)
