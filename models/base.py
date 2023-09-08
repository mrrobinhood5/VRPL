from beanie import Document, Indexed, BackLink, Link
from typing import Optional, List, Union
from pydantic import confloat, EmailStr, AnyUrl, Field, HttpUrl, BaseModel, AnyHttpUrl
from pydantic_core import Url
from models.enums import Location, Region, MapTypes, TournamentParticipation
from datetime import datetime
from pymongo import ASCENDING



def url_to_str(v: Url):
    return str(v)


class VRPLObject(Document):
    pass


class GameBase(VRPLObject):
    name: str
    description: Optional[str] = None
    link: Optional[AnyUrl] = None

    players: Optional[list[BackLink['PlayerBase']]] = Field(default_factory=list, original_field='games')
    teams: Optional[list[BackLink['TeamBase']]] = Field(default_factory=list, original_field='game')
    casters: Optional[list[BackLink['CasterBase']]] = Field(default_factory=list, original_field='games')
    maps: Optional[list[BackLink['MapBase']]] = Field(default_factory=list, original_field='game')
    tournaments: Optional[list[BackLink['TournamentBase']]] = Field(default_factory=list, original_field='game')

    class Settings:
        bson_encoders = {Url: url_to_str}
        is_root = True

class PlayerBase(VRPLObject):
    discord_id: Indexed(int, unique=True)
    name: Indexed(str, unique=True)
    game_uid: Indexed(str, unique=True)
    height: confloat(ge=4.0, le=6.0)
    location: Location
    registered_on: datetime = datetime.now()
    alias: Optional[list[str]] = Field(default_factory=list)
    promo_email: Optional[EmailStr] = None
    is_banned: bool = False
    is_suspended: bool = False

    games: Optional[list[Link[GameBase]]] = Field(default_factory=list)
    caster: Optional[BackLink['CasterBase']] = Field(original_field='player')  # dont think this is necessary
    teams: Optional[list[BackLink["TeamBase"]]] = Field(original_field='members', default_factory=list)
    tournaments: Optional[list[BackLink['TournamentBase']]] = Field(original_field='participants', default_factory=list)
    matches: Optional[list[BackLink["MatchBase"]]] = Field(original_field='participants', default_factory=list)
    reprimands: Optional[list[BackLink['ReprimandBase']]] = Field(original_field='recipient', default_factory=list)

    @property
    def mmr(self):
        return False

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True


class CasterBase(VRPLObject):
    links: List[HttpUrl]
    logo: Optional[AnyUrl] = None
    approved: bool = False

    player: Link[PlayerBase]
    broadcasts: Optional[list[BackLink['BroadcastBase']]] = Field(original_field='caster', default_factory=list)

    game: Link[GameBase]

    class Settings:
        bson_encoders = {Url: url_to_str}
        is_root = True

class TeamBase(VRPLObject):
    name: Indexed(str, unique=True)
    region: Region
    motto: Optional[str] = None
    logo: Optional[AnyUrl] = None
    active: bool = True
    registered_on: datetime = datetime.now()

    members: List[Link[PlayerBase]]  # will always have a captain
    game: Link[GameBase]

    tournaments: Optional[list[BackLink["TournamentBase"]]] = Field(original_field="participants")
    matches: Optional[List[BackLink["MatchBase"]]] = Field(original_field="participants")
    reprimands: Optional[List[BackLink["ReprimandBase"]]] = Field(original_field="recipient")


    @property
    def mmr(self):
        return True

    @property
    def length(self):
        return len(self.members)

    class Settings:
        bson_encoders = {Url: url_to_str}
        is_root = True

    class Config:
        arbitrary_types_allowed = True


class MapBase(VRPLObject):
    name: Indexed(str, unique=True)
    image: AnyUrl

    game: Link[GameBase]

    tournaments: Optional[list[BackLink['TournamentBase']]] = Field(original_field="maps")
    weeks: Optional[list[BackLink['WeekBase']]] = Field(original_field='maps')
    matches: Optional[list[BackLink['MatchBase']]] = Field(original_field="maps")

    class Settings:
        bson_encoders = {Url: url_to_str}
        is_root = True

class TournamentBase(VRPLObject):
    name: Indexed(str, unique=True)
    description: str
    prizes: str
    active: bool
    is_joinable: bool

    start_date: datetime
    round_frequency: int  # in days
    next_round: datetime

    maps_per_round: int
    map_types: MapTypes
    no_repeat_maps_for: int  # in weeks
    elimination: bool
    participation: TournamentParticipation

    # participants: list[Link[VRPLObject]]
    game: Link[GameBase]

    weeks: Optional[list[BackLink['WeekBase']]] = Field(original_field="tournament", default_factory=list)
    matches: Optional[list[BackLink['MatchBase']]] = Field(original_field="tournament", default_factory=list)
    maps: Optional[list[Link[MapBase]]] = Field(default_factory=list)

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True

    @property
    def last_week(self):
        w = self.weeks
        return w[-1]

    @property
    def first_week(self):
        w = self.weeks
        return w[0]



class WeekBase(VRPLObject):
    order: int  # increment
    start_date: datetime
    end_date: datetime

    tournament: Link[TournamentBase]
    maps: list[Link['MapBase']]

    matches: Optional[list[BackLink['MatchBase']]] = Field(original_field='week')

    class Settings:
        is_root = True





class MatchBase(VRPLObject):
    # home: Union[TeamBase, PlayerBase]  # These can be properties?
    # away: Union[TeamBase, PlayerBase]
    match_date: Optional[datetime] = None

    week: Link[WeekBase]
    tournament: Link[TournamentBase]
    maps: list[Link[MapBase]]
    # participants: list[Link[VRPLObject]]

    scores: Optional[list[BackLink['ScoreBase']]] = Field(original_field="match")
    broadcast: Optional[BackLink['BroadcastBase']] = Field(original_field="match")

    class Settings:
        is_root = True


class ScoreBase(VRPLObject):
    score: int
    screenshot: AnyUrl
    approved: bool  # this may not be needed, approval should create the score base otherwise it wouldn't exist

    match: Link[MatchBase]
    # submitter: Link[VRPLObject]  # Implement Properly
    # approver: Link[VRPLObject]  # Implement Properly

    class Settings:
        bson_encoders = {Url: url_to_str}
        is_root = True


class ReprimandBase(VRPLObject):
    text: str
    reference_ticket: AnyUrl

    recipient: Link[TeamBase]

    class Settings:
        bson_encoders = {Url: url_to_str}
        is_root = True


class BroadcastBase(VRPLObject):
    link: AnyUrl

    match: Link[MatchBase]
    caster: Link[CasterBase]

    class Settings:
        bson_encoders = {Url: url_to_str}
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
    # requestor: Link[VRPLObject]
    # target: Link[VRPLObject]
    property: str
    action: Union[str, bool, int, datetime]
    # approver: Link[VRPLObject]
    date_requested: Indexed(datetime, index_type=ASCENDING) = datetime.now()

    game: Link[GameBase]

    class Settings:
        is_root = True

    class Config:
        arbitrary_types_allowed = True
