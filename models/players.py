from .base import (PlayerBase, TeamBase, TournamentBase, MatchBase,
                   ReprimandBase, CasterBase)
from pydantic import BaseModel, Field
from beanie import View


class LeadershipMixin(BaseModel):
    @property
    def captain(self):
        return isinstance(self, CaptainPlayer)

    @property
    def co_captain(self):
        return isinstance(self, CoCaptainPlayer)


class NormalPlayer(PlayerBase, LeadershipMixin):
    ...


class CaptainPlayer(PlayerBase, LeadershipMixin):
    ...


class CoCaptainPlayer(PlayerBase, LeadershipMixin):
    ...


class AllPlayerLocations(View):
    name: str = Field(alias='_id')
    players: list[str]

    class Settings:
        source = PlayerBase
        pipeline = [
            {'$group': {'_id': '$location', 'players': {'$push': '$name'}}}
        ]