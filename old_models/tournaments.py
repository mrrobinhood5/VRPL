from beanie import Document, BackLink
from old_models.base import Base
from old_models.players import PlayerModel
from old_models.teams import TeamModel
from typing import Optional

class TournamentModel(Document, Base):
    players: Optional[BackLink[PlayerModel]]
    teams: Optional[BackLink[TeamModel]]
