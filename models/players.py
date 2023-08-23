from .base import (PlayerBase, TeamBase, TournamentBase, MatchBase,
                   ReprimandBase, CasterBase)


class NormalPlayer(PlayerBase):
    captain = False
    co_captain = False


class CaptainPlayer(PlayerBase):
    captain = True
    co_captain = False


class CoCaptainPlayer(PlayerBase):
    captain = False
    co_captain = True
