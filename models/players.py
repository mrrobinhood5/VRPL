from .base import (PlayerBase, TeamBase, TournamentBase, MatchBase,
                   ReprimandBase, CasterBase)


class NormalPlayer(PlayerBase):
    captain: bool = False
    co_captain: bool = False


class CaptainPlayer(PlayerBase):
    captain: bool = True
    co_captain: bool = False


class CoCaptainPlayer(PlayerBase):
    captain: bool = False
    co_captain: bool = True
