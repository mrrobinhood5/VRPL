import asyncio

from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from classes.players import PlayerModel, UpdatePlayerModel, PlayerTeamModel, UpdatePlayerTeamModel
from classes.teams import TeamModel, UpdateTeamModel
from typing import List
from config import BOT_TOKEN, INTENTS, BOT_PREFIX
from discord.ext import commands

import discord
from database import db_count_items, db_find_one_by_other, db_delete_one, db_add_one, db_find_all, db_find_one, db_update_one, db_find_some, db
import uvicorn

app = FastAPI()
bot = commands.Bot(command_prefix=BOT_PREFIX, description='VRPL Team Manager', intents=INTENTS)

@app.get('/')
def read_root():
    """
    This Build Testing V2 creates
    - **5** Teams  *(Randomly Generated)*
    - **30** Players *(Randomly Generated)*

    Every restart, all the stats get rebuild from scratch.

    **THIS IS FOR TESTING AND PROOF OF CONCEPT ONLY**
    """
    return {"Testing": "ok"}


@app.post("/player/", response_description="Register a new Player", response_model=PlayerModel)
async def register_player(player: PlayerModel = Body(...)):
    """ To register a Player, you only need to send in
    ```"name" : "Chosen Name to be used in-game",
    "discord_id": "DISCORD_ID from the discord API",
    "game_uid": "uid from c$",
    "height": "5ft 6in"``` """
    if await db_find_one_by_other('players', {'discord_id': player.discord_id}) is not None:
        raise HTTPException(status_code=406, detail=f"Discord ID {player.discord_id} already Registered")
    created_player = await db_add_one('players', player)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@app.get("/players", response_description="List all registered players", response_model=List[PlayerModel])
async def list_players(n: int = 100):
    """ Lists all registered players from the DB """
    players = await db_find_all("players", n)
    return players


@app.get("/player/{id}", response_description="Get a single player", response_model=PlayerModel)
async def show_player(id: str):
    """ To retrieve a single player, send in just the ObjectID for the player. You can also send in the Discord ID """
    if (player := await db_find_one("players", id)) is not None:
        return player
    if (player := await db_find_one_by_other('players', {'discord_id': id})) is not None:
        return player
    raise HTTPException(status_code=404, detail=f"Player {id} not found")


@app.put("/player/{id}", response_description="Update a player", response_model=PlayerModel)
async def update_player(id: str, player: UpdatePlayerModel = Body(...)):
    """ Updatable fields are:
    ```"name": "If you are planning on changing the in-game name",
    "email": "to make email updates",
    "game_uid": "to make corrections to the UID"```
    """
    player = {k: v for k, v in player.dict().items() if v is not None}
    if len(player) >= 1:
        update_result = await db_update_one('players', id, player)
        if update_result.modified_count == 1:
            if (updated_player := await db_find_one('players', id)) is not None:
                return updated_player
    if existing_player := await db_find_one('players', id) is not None:
        return existing_player
    raise HTTPException(status_code=404, detail=f"Player {id} not found")


@app.post("/team/", response_description="Register a new Team", response_model=TeamModel)
async def register_team(team: TeamModel = Body(...)):
    """ To register a team you need to send in:
    ```"name": "Official Team Name",
    "captain": "The captains Player ObjectID",
    "team_motto": "A brief Motto"```
    """
    if await db_find_some('teams', {'name': team.name}):
        raise HTTPException(status_code=406, detail=f"{team.name} is already a Team")

    if await db_find_some('teams', {'$or': [{'captain': str(team.captain)}, {'co_captain': str(team.captain)}]}):
        raise HTTPException(status_code=406, detail=f"{team.captain} is already a captain or co-captain of a team")

    created_team = await db_add_one('teams', team)
    await request_to_join_team(PlayerTeamModel(
        team=created_team['_id'],
        player=created_team['captain'],
        approved=True))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_team)


@app.get("/teams", response_description="List all registered teams", response_model=List[TeamModel])
async def list_teams(n: int = 100):
    """ Lists all registered teams """
    teams = await db_find_all('teams', n)
    return teams


@app.get("/team/{id}", response_description="Get a single Team", response_model=TeamModel)
async def show_team(id: str):
    """ To retrieve a specific team, provide the Team ObjectID """
    if (team := await db_find_one('teams', id)) is not None:
        return team
    raise HTTPException(status_code=404, detail=f"Team {id} not found")


@app.put("/team/{id}", response_description="Update a team", response_model=TeamModel)
async def update_team(id: str, team: UpdateTeamModel = Body(...)):
    """ The following team fields can be updated:
     ```"name" : "Updated team name",
     "team_motto": "Updated team motto",
     "captain": "provide 1 Player ObjectID for new captain",
     "team_logo": "url for a team logo image",
     "co_captain": "player ObjectID for a co-captain. They can also make changes to the team"
     "active": False or True to mark as active``` """
    team = {k: v for k, v in team.dict().items() if v is not None}
    if len(team) >= 1:
        if 'co_captain' in team.keys():
            team['co_captain'] = str(team['co_captain'])
            if team['co_captain'] not in [x['_id'] for x in await list_team_players(id)]:
                raise HTTPException(status_code=406, detail=f"That Player is not a member of the team")

        update_result = await db_update_one('teams', id, team)
        if update_result.modified_count == 1:
            if (updated_team := await db_find_one('team', id)) is not None:
                return updated_team
    if (existing_team := await db_find_one('teams', id)) is not None:
        return existing_team
    raise HTTPException(status_code=404, detail=f"Team {id} not found")


@app.get("/team/{id}/approvals", response_description="List all pending Approvals",
         response_model=List[PlayerTeamModel])
async def list_pending_approvals(id: str):
    """
    Lists pending approvals by team
    """
    # results = await db_find_some("player_team_link", {"team": {"$eq": id}, "approved": {"$ne": True}})
    results = await db_find_some("player_team_link", {"team": id, "approved": None})
    return results


@app.get("/approvals", response_description="List ALL pending Approvals", response_model=List[PlayerTeamModel])
async def list_all_pending_approvals():
    """ Lists ALL Pending Approvals on the server"""
    results = await db_find_some('player_team_link', {"approved": None})
    return results


@app.get("/team/{id}/players", response_description="List all Players in a Team", response_model=List[PlayerModel])
async def list_team_players(id: str):
    players = await db_find_some('player_team_link', {'team': id, 'approved': True}, {'player': 1, '_id': 0})
    players = [await db_find_one('players', player['player']) for player in players]
    return players


@app.put("/team/join/", response_description="Request to Join a Team", response_model=PlayerTeamModel)
async def request_to_join_team(request: PlayerTeamModel = Body(...)):
    """ To request to join a team, a player creates a request
     and a team captain or cocaptain has to approve it """
    if not await db_find_some('player_team_link', {'player': str(request.player), 'team': str(request.team)}):
        created_player = await db_add_one("player_team_link", request)
    else:
        raise HTTPException(status_code=406, detail="A similar request has already been submitted")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@app.put("/team/approve/{id}", response_description="Approve a team join", response_model=PlayerTeamModel)
async def approve_team_join(id: str, request: UpdatePlayerTeamModel = Body(...)):
    """ Approve or Decline a team join. send a {"approved":true} or {"approved":false} """
    if request.approved is None or len(request.dict().items()) == 0:
        raise HTTPException(status_code=402, detail=f"You must send {{'approved':true}} or {{'approved':false}}")

    if (current_request := await db_find_one('player_team_link', id)) is not None: # found the request
        # check the team count for max
        if await db_count_items('player_team_link', {'team': current_request['team'], 'approved': True}) >= 5:
            raise HTTPException(status_code=402, detail=f'Team is full!')
        # not at max
        else:
            update_result = await db_update_one('player_team_link', id, request.dict())
            if update_result.modified_count == 1:
                if (updated_request := await db_find_one('player_team_link', id)) is not None:
                    return updated_request
    else:
        raise HTTPException(status_code=404, detail=f"Team Join request {id} not found") # did not find the request


@app.delete("/team/remove/{id}", response_description="Remove a Player from Team")
async def remove_player(id: str):
    delete_result = await db_delete_one('player_team_link', id)
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=delete_result)
    raise HTTPException(status_code=404, detail=f'Player {id} not found')


@app.get('/team/{team_id}/captains', response_description='Get the teams captain / co-captain', response_model=List[PlayerModel])
async def get_captains(team_id: str):
    team = await db_find_one('teams', team_id)
    captains = await db_find_some('players', { '$or': [
        {'_id': team['captain']}, {'_id': team['co_captain']} ]})
    return captains


@app.get("/db/drop")
async def drop_db():
    for coll in await db.list_collection_names():
        await db.drop_collection(coll)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID: {bot.user.id})')
    activity = discord.Game('Contractor$ on Quest 3')
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.command()
async def hello(ctx: commands.Context):
    """ Just says Hello"""
    await ctx.reply(f'### Well hello to you too {ctx.author.name}')


async def is_owner(ctx):
    return ctx.author == ctx.guild.owner


@bot.command(name='purge')
@commands.check(is_owner)
async def clear_channel(ctx: commands.Context, amount: int = 100):

    deleted = await ctx.channel.purge(limit=amount, reason='Owner Purge', bulk=True)
    await ctx.send(f'{ctx.author.mention} requested `{amount}` messages deleted and `{len(deleted)}` were actually deleted. **I can only do 100 at a time** \n '
                   f'If you need more, please re-run the command. ')


@app.on_event('startup')
async def run_bot():
    asyncio.create_task(bot.start(BOT_TOKEN))


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8080, reload=True)
