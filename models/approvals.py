from models.base import ApprovalBase, PlayerBase, TeamBase, MatchBase, ScoreBase, CasterBase, VRPLObject
from datetime import datetime
from beanie import Link


class TeamJoinApproval(ApprovalBase):
    requestor: Link[PlayerBase]
    target: Link[TeamBase]
    property: str = 'members'
    action: PlayerBase
    approver: list[Link[PlayerBase]]


class MatchDateApproval(ApprovalBase):
    requestor: Link[PlayerBase]
    target: Link[MatchBase]
    property: str
    action: datetime
    approver: list[Link[PlayerBase]]


class PlayerScoreApproval(ApprovalBase):
    requestor: Link[PlayerBase]
    target: ScoreBase
    property: str = 'approved'
    action: bool = True
    approver: Link[PlayerBase]


class TeamScoreApproval(ApprovalBase):
    requestor: Link[TeamBase]
    target: ScoreBase
    property: str = 'approved'
    action: bool = True
    approver: Link[TeamBase]  # maybe?


class CasterRequestApproval(ApprovalBase):
    requestor: Link[PlayerBase]
    target: Link[CasterBase]
    property: str = 'approved'
    action: bool = True
    approver: Link[VRPLObject]  # Need to make Admin Mixins
