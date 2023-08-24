from .base import TeamBase, PlayerBase, TournamentBase, MatchBase, ReprimandBase


class StandardTeam(TeamBase):
    max_size: int = 10


class MiniTeam(TeamBase):
    max_size: int = 5

