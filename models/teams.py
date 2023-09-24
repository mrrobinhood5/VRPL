from .base import TeamBase, PlayerBase, TournamentBase, MatchBase, ReprimandBase
from pydantic import BaseModel, Field
from beanie import View
from monggregate import Pipeline, S

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


class AllTeamMembersByTeam(View):
    name: str = Field(alias='_id')
    members: list[str]

    class Settings:
        source = TeamBase
        pipeline = (Pipeline()
                    .lookup(right='PlayerBase', right_on='_id', left_on='members.$id', name='members')
                    .unwind('$members')
                    .group(by='$name', query={'members': S.push('$members.name')})
                    .export())
