from fastapi import APIRouter
from classes.teams import TeamModel, UpdateTeamModel
from classes.players import PlayerTeamModel, PlayerModel, UpdatePlayerTeamModel
from fastapi import Body, HTTPException, status
from fastapi.responses import JSONResponse
from database import db_delete_one, db_count_items, db_find_some, db_add_one, db_find_all, db_find_one, db_update_one

router = APIRouter(tags=['teams'], prefix='/teams')


@router.post("/register", response_description="Register a new Team", response_model=TeamModel)
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
    await request_to_join_team(str(team.id), PlayerTeamModel(
        team=created_team['_id'],
        player=created_team['captain'],
        approved=True))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_team)


@router.get("/all", response_description="List all registered teams", response_model=list[TeamModel])
async def list_teams(n: int = 100) -> list[dict]:
    """ Lists all registered teams """
    teams = await db_find_all('teams', n)
    return teams


@router.get("/{team_id}", response_description="Get a single Team", response_model=TeamModel)
async def show_team(team_id: str):
    """ To retrieve a specific team, provide the Team ObjectID """
    if (team := await db_find_one('teams', team_id)) is not None:
        return team
    raise HTTPException(status_code=404, detail=f"Team {team_id} not found")


@router.put("/{team_id}", response_description="Update a team", response_model=TeamModel)
async def update_team(team_id: str, team: UpdateTeamModel = Body(...)):
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
            if team['co_captain'] not in [x['_id'] for x in await list_team_players(team_id)]:
                raise HTTPException(status_code=406, detail=f"That Player is not a member of the team")

        update_result = await db_update_one('teams', team_id, team)
        if update_result.modified_count == 1:
            if (updated_team := await db_find_one('team', team_id)) is not None:
                return updated_team
    if (existing_team := await db_find_one('teams', team_id)) is not None:
        return existing_team
    raise HTTPException(status_code=404, detail=f"Team {team_id} not found")


@router.get("/{team_id}/players", response_description="List all Players in a Team", response_model=list[PlayerModel],
            tags=['players'])
async def list_team_players(team_id: str):
    players = await db_find_some('player_team_link', {'team': team_id, 'approved': True}, {'player': 1, '_id': 0})
    players = [await db_find_one('players', player['player']) for player in players]
    return players


@router.post("/{team_id}/join", response_description="Request to Join a Team", response_model=PlayerTeamModel)
async def request_to_join_team(team_id: str, request: PlayerTeamModel = Body(...)):
    """ To request to join a team, a player creates a request
     and a team captain or co-captain has to approve it """
    # check to see if it is a valid team
    if not await db_find_one('teams', team_id, {'active': 1}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='That team is not found')
    if not await db_find_some('player_team_link', {'player': str(request.player), 'team': team_id}):
        request.team = team_id
        created_player = await db_add_one("player_team_link", request)
    else:
        raise HTTPException(status_code=406, detail="A similar request has already been submitted")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_player)


@router.put("/approve/{approval_id}", response_description="Approve a team join", response_model=PlayerTeamModel,
            tags=['approvals'])
async def approve_team_join(approval_id: str, request: UpdatePlayerTeamModel = Body(...)):
    """ Approve or Decline a team join. send a {"approved":true} or {"approved":false} """
    if request.approved is None or len(request.dict().items()) == 0:
        raise HTTPException(status_code=406, detail=f"You must send {{'approved':true}} or {{'approved':false}}")
    if (current_request := await db_find_one('player_team_link', approval_id)) is not None:  # found the request
        # check the team count for max
        if await db_count_items('player_team_link', {'team': current_request['team'], 'approved': True}) >= 10:
            raise HTTPException(status_code=406, detail=f'Team is full!')
        else:
            update_result = await db_update_one('player_team_link', approval_id, request.dict())
            if update_result.modified_count == 1:
                if (updated_request := await db_find_one('player_team_link', approval_id)) is not None:
                    return updated_request
    else:
        raise HTTPException(status_code=404, detail=f"Team Join request {approval_id} not found")


@router.delete("/remove/player/{player_id}", response_description="Remove a Player from Team",
               tags=['players'])
async def remove_player(player_id: str):
    delete_result = await db_delete_one('player_team_link', player_id)
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=delete_result)
    raise HTTPException(status_code=404, detail=f'Player {player_id} not found')


@router.get('/{team_id}/captains', response_description='Get the teams captain / co-captain',
            response_model=list[PlayerModel])
async def get_captains(team_id: str):
    team = await db_find_one('teams', team_id)
    captains = await db_find_some('players', {'$or': [
        {'_id': team['captain']}, {'_id': team['co_captain']}]})
    return captains


@router.get('/{team_id}/members', response_description='Get the team members', response_model=list[PlayerModel])
async def get_team_members(team_id: str):
    player_list = await db_find_some('player_team_link', {'team': team_id}, exclude={'player': 1})
    player_list = [await db_find_one('players', player['player']) for player in player_list]
    return player_list
