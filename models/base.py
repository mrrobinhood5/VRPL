from beanie import Document, Indexed, BackLink, Link
from typing import Optional, List, Union
from pydantic import confloat, EmailStr, HttpUrl, Field
from models.enums import Location, Region, MapTypes, TournamentParticipation
from datetime import datetime


class VRPLObject(Document):
    pass


class PlayerBase(VRPLObject):
    discord_id: Indexed(int, unique=True)
    name: Indexed(str, unique=True)
    game_uid: str
    height: confloat(ge=4.0, le=6.0)
    location: Location
    registered_date: datetime
    alias: Optional[list[str]]
    promo_email: Optional[EmailStr]
    is_banned: bool = False
    is_suspended: bool = False

    caster: Optional[BackLink['CasterBase']] = Field(original_field='player')
    teams: Optional[list[BackLink["TeamBase"]]] = Field(original_field='members')
    tournaments: Optional[list[BackLink['TournamentBase']]] = Field(original_field='participants')
    matches: Optional[list[BackLink["MatchBase"]]] = Field(original_field='participants')
    reprimands: Optional[list[BackLink['ReprimandBase']]] = Field(original_field='recipient')

    @property
    def mmr(self):
        return False

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True


class CasterBase(VRPLObject):
    twitch: HttpUrl
    youtube: HttpUrl
    logo: HttpUrl
    approved: bool = False

    player: Link[PlayerBase]
    broadcasts: Optional[list[BackLink['BroadcastBase']]] = Field(original_field='caster')


class TeamBase(VRPLObject):
    name: Indexed(str, unique=True)
    region: Region
    motto: str
    logo: HttpUrl
    active: bool
    created: datetime

    members: List[PlayerBase]  # will always have a captain

    tournaments: Optional[list[BackLink["TournamentBase"]]] = Field(original_field="participants")
    matches: Optional[List[BackLink["MatchBase"]]] = Field(original_field="participants")
    reprimands: Optional[List[BackLink["ReprimandBase"]]] = Field(original_field="recipient")

    @property
    def mmr(self):
        return True

    @property
    def leadership(self) -> list[Union['PlayerCaptain', 'PlayerCoCaptain']]:
        return []

    @property
    def captain(self) -> 'PlayerCaptain':
        return True

    @property
    def co_captain(self) -> 'PlayerCoCaptain':
        return True

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True


class TournamentBase(VRPLObject):
    name: Indexed(str, unique=True)
    description: str
    start_date: datetime
    prizes: str
    active: bool
    is_joinable: bool
    round_frequency: int  # in days
    next_round: datetime
    maps_per_round: int
    map_types: MapTypes
    elimination: bool
    participation: TournamentParticipation

    participants: list[Link[VRPLObject]]

    weeks: Optional[list[BackLink['WeekBase']]] = Field(original_field="tournament")
    matches: Optional[list[BackLink['MatchBase']]] = Field(original_field="tournament")
    maps: Optional[list[BackLink['MapBase']]] = Field(original_field="maps")

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True


class WeekBase(VRPLObject):
    order: int  # increment
    start_date: datetime
    end_date: datetime

    tournament: Link[TournamentBase]
    maps: list[Link['MapBase']]

    matches: Optional[list[BackLink['MatchBase']]] = Field(original_field='week')

    class Settings:
        is_root = True


class MapBase(VRPLObject):
    name: Indexed(str, unique=True)
    image: HttpUrl

    tournaments: Optional[list[BackLink[TournamentBase]]] = Field(original_field="maps")
    weeks: Optional[list[BackLink[WeekBase]]] = Field(original_field='maps')
    matches: Optional[list[BackLink['MatchBase']]] = Field(original_field="maps")

    class Settings:
        is_root = True


class MatchBase(VRPLObject):
    # home: Union[TeamBase, PlayerBase]  # These can be properties?
    # away: Union[TeamBase, PlayerBase]
    match_date: Optional[datetime]

    week: Link[WeekBase]
    tournament: Link[TournamentBase]
    maps: list[Link[MapBase]]
    participants: list[Link[PlayerBase]]

    scores: Optional[list[BackLink['ScoreBase']]] = Field(original_field="match")
    broadcast: Optional[BackLink['BroadcastBase']] = Field(original_field="match")

    class Settings:
        is_root = True


class ScoreBase(VRPLObject):
    score: int
    screenshot: HttpUrl
    approved: bool  # this may not be needed, approval should create the score base otherwise it wouldn't exist

    match: Link[MatchBase]
    submitter: Link[VRPLObject]  # Implement Properly
    approver: Link[VRPLObject]  # Implement Properly

    class Settings:
        is_root = True


class ReprimandBase(VRPLObject):
    text: str
    reference_ticket: HttpUrl

    recipient: Link[TeamBase]

    class Settings:
        is_root = True


class BroadcastBase(VRPLObject):
    link: HttpUrl

    match: Link[MatchBase]
    caster: Link[CasterBase]

    class Settings:
        is_root = True


class SettingsBase(VRPLObject):
    channel_id: int
    message_id: int

    class Settings:
        is_root = True


class ApprovalBase(VRPLObject):
    """ Concept of approvals:
    Requestor is the Object who wants something approved. It could be a Team or a Player. This is for reference.
    Target is the Object that needs to be changed.
    Property is the attribute from the Target that will be changed.
    Action is the change itself. The boolean or thing that will be inserted into the Target's Property.
    Approver is the person who will click YES to complete the action.
    """
    requestor: Link[VRPLObject]
    target: Link[VRPLObject]
    property: str
    action: Union[str, bool, int, datetime]
    approver: Link[VRPLObject]
    date_complete: Optional[datetime]

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True
