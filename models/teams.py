from .base import TeamBase, PlayerBase, TournamentBase, MatchBase, ReprimandBase
from pydantic import BaseModel


class LeadershipMixin(BaseModel):

    @property
    def captain(self):
        for member in self.members:
            if member.captain:
                return member
        return None

    @property
    def co_captain(self):
        for member in self.members:
            if member.co_captain:
                return member
        return None

    @property
    def leadership(self):
        return [member for member in self.members if member.captain or member.co_captain]


class StandardTeam(TeamBase, LeadershipMixin):
    max_size: int = 10


class MiniTeam(TeamBase, LeadershipMixin):
    max_size: int = 5

