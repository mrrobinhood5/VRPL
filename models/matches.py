from beanie import Link
from .base import MatchBase, PlayerBase, TeamBase, WeekBase, TournamentBase, MapBase, ScoreBase, BroadcastBase


class PlayerMatch(MatchBase):
    participants: list[Link[PlayerBase]]


class TeamMatch(MatchBase):
    participants: list[Link[TeamBase]]
