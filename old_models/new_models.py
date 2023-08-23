import beanie
import discord
import pymongo

from beanie import Document, Indexed, Link, BackLink
from pydantic import confloat, EmailStr, Field, BaseModel, FileUrl, validator
from typing import Optional, List
from custom import bot, VRPLBot


class Base(BaseModel):
    _bot = bot

    @property
    def bot(self) -> VRPLBot:
        return self._bot

class PlayerModel(Document, Base):
    """ PlayerModel is the representation of a registered player in the league """
    discord_id: int
    name: Indexed(str, pymongo.TEXT)
    game_uid: str  # REFACTOR: can game UIDs be validated
    calibrated_height: confloat(gt=4.5, lt=6.5)  # TODO: validate within the parameters allowed
    promo_email: Optional[EmailStr]

    is_banned: bool = False
    is_suspended: bool = False
    mmr: int = 0

    tournaments = Optional[Link['TournamentModel']]
    team: Optional[BackLink['TeamModel']] = Field(original_field='members')
    discord_user: Optional[discord.User] = Field(default=None, exclude=True)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    class Settings:
        name = "players"


class TeamModel(Document, Base):
    """ Team Model is the representation of a full team. In code, it will include full members
    in database it will only include ObjectIDs"""
    name: Indexed(str, index_type=pymongo.TEXT)
    motto: str
    logo: Optional[FileUrl]
    captain: Link[PlayerModel]
    co_captain: Optional[Link[PlayerModel]]
    members: Optional[List[Link[PlayerModel]]]

    active: bool = True
    mmr: int = 0

    @validator('members', always=True)
    def check_members(cls, v, values):
        """ Checks to see if Captain / Co-Captain are listed as members """
        if cpt := values.get('captain') not in v:
            return [cpt]
        else:
            return v

class PlayerTeamLink(Document):
    """ PlayerTeamLinkModel stores the links between players and teams.
    This is essentially the TeamJoin Approvals """
    player: Link[PlayerModel]
    team: Link[TeamModel]
    approved: bool = False

class TeamMembersView(beanie.View): # This may not be needed because we are backlinking members from players model
    team: str = Field(alias="name")
    members: list[PlayerModel]

    class Settings:
        source = PlayerTeamLink
        pipeline = [{"$group": {
            
        }}]
