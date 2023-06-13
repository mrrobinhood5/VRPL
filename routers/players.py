from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse

from models.players import PlayerModel, UpdatePlayerModel
from models.teams import TeamModel
from models.teamplayers import FullTeamModel
from typing import Union

from database import db_find_one_by_other, db_add_one, db_find_all, db_find_one, db_update_one, db_update_one_discord

router = APIRouter(tags=['players'], prefix='/players')


@router.post("/register", response_description="Register a new Player",
             response_model=PlayerModel)
async def register_player(player: PlayerModel = Body(...)):
    """ To register a Player, you only need to send in
    ```"name" : "Chosen Name to be used in-game",
    "discord_id": "DISCORD_ID from the discord API",
    "game_uid": "uid from c$",
    "height": "5ft 6in"``` """
    if await db_find_one_by_other('players', {'discord_id': player.discord_id}) is not None:
        raise HTTPException(status_code=406, detail=f"Discord ID is already already Registered")
    created_player = await db_add_one('players', player)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@router.get("/all", response_description="List all registered players", response_model=list[PlayerModel])
async def list_players(n: int = 100):
    """ Lists all registered players from the DB """
    players = await db_find_all("players", n)
    return players


@router.get("/{player_id}/team", response_description="Get a Players Team", response_model=TeamModel)
async def get_player_team(player_id: str) -> dict:
    """ Retrieve the team the player belongs to """
    # check to see if you got a discord id:
    if discord_player := await db_find_one_by_other('players', {'discord_id': player_id}):
        player_id = discord_player.get('_id')
    player_link = await db_find_one_by_other('player_team_link', {'player': player_id, 'approved': True})
    if not player_link:
        raise HTTPException(status_code=404, detail=f'You do not belong to any teams')
    team = await db_find_one('teams', player_link['team'])
    return team


@router.get("/{player_id}", response_description="Get a single player", response_model=PlayerModel)
async def show_player(player_id: str) -> dict:
    """ To retrieve a single player, send in just the ObjectID for the player. You can also send in the Discord ID """
    if (player := await db_find_one("players", player_id)) is not None:
        return player
    if (player := await db_find_one_by_other('players', {'discord_id': player_id})) is not None:
        return player
    raise HTTPException(status_code=404, detail=f"Player is not registered")


@router.put("/{player_id}", response_description="Update a player", response_model=PlayerModel)
async def update_player(player_id: str, player: UpdatePlayerModel = Body(...)):
    """ Updatable fields are:
    ```"name": "If you are planning on changing the in-game name",
    "email": "to make email updates",
    "game_uid": "to make corrections to the UID"```
    """
    player = {k: v for k, v in player.dict().items() if v is not None}  # remove the Nones
    if len(player) >= 1:
        update_result = await db_update_one('players', player_id, player)
        if update_result.modified_count == 1:
            if (updated_player := await db_find_one('players', player_id)) is not None:
                return updated_player
        else:  # if it cannot be found with obj_id try discord_id
            update_result = await db_update_one_discord('players', player_id, player)
            if update_result.modified_count == 1:
                if (updated_player := await db_find_one_by_other('players', {'discord_id': player_id})) is not None:
                    return updated_player
    if (existing_player := await db_find_one('players', player_id)) is not None:
        return existing_player
    raise HTTPException(status_code=404, detail=f"Player {player_id} not found")


