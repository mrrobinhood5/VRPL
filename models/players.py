from .base import (PlayerBase, TeamBase, TournamentBase, MatchBase,
                   ReprimandBase, CasterBase)
from pydantic import BaseModel


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
