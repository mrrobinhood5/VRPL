from fastapi import APIRouter
from classes.players import PlayerTeamModel
from database import db_find_some

router = APIRouter(tags=['approvals'])


@router.get("/teams/{approval_id}/approvals", response_description="List all pending Approvals",
            response_model=list[PlayerTeamModel], tags=['teams'])
async def list_pending_approvals(approval_id: str):
    """
    Lists pending approvals by team
    """
    results = await db_find_some("player_team_link", {"team": approval_id, "approved": None})
    return results


@router.get("/approvals/pending", response_description="List ALL pending Approvals",
            response_model=list[PlayerTeamModel])
async def list_all_pending_approvals():
    """ Lists ALL Pending Approvals on the server"""
    results = await db_find_some('player_team_link', {"approved": None})
    return results
