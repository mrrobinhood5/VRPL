from fastapi import APIRouter
from models.players import PlayerTeamModel
from database import db_find_some

router = APIRouter(tags=['approvals'])


@router.get("/approvals/pending", response_description="List ALL pending Approvals",
            response_model=list[PlayerTeamModel])
async def list_all_pending_approvals():
    """ Lists ALL Pending Approvals on the server"""
    results = await db_find_some('player_team_link', {"approved": None})
    return results
