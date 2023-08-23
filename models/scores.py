from .base import ScoreBase, TeamBase, PlayerBase, MatchBase, VRPLObject
from beanie import Link


class TeamScore(ScoreBase):
    submitter: Link[TeamBase]
    approver: Link[TeamBase]


class PlayerScore(ScoreBase):
    submitter: Link[PlayerBase]
    approver: Link[PlayerBase]
