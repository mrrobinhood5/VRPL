from pydantic import HttpUrl, Field
from classes.base import Base, PyObjectId

from typing import Optional, Union
import discord


class TeamModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    team_motto: str
    captain: PyObjectId
    team_logo: Optional[HttpUrl]
    co_captain: Optional[Union[PyObjectId, None]] = None
    active: bool = True
    team_mmr: int = 0

    class Config:
        schema_extra = {
            "example": {
                "name": "Team Name",
                "captain": "ObjectID",
                "team_motto": "We are Great!"
            }
        }


class UpdateTeamModel(Base):
    name: Optional[str]
    team_motto: Optional[str]
    captain: Optional[PyObjectId]
    team_logo: Optional[HttpUrl]
    co_captain: Optional[PyObjectId]
    active: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "name": "New Team Name",
                "team_motto": "We are still great!",
                "captain": "ObjectID",
                "co_captain": '646e67d8019b9ae38b4d4647',
                "active": True
            }
        }


class NewTeamEmbed(discord.Embed):

    def __init__(self, inter: discord.Interaction, team: dict):
        super().__init__(title=team['name'], description=team['team_motto'])
        self.color = discord.Color.blurple()
        self.set_thumbnail(url=team.get('team_logo', "https://cdn.discordapp.com/emojis/1058108114626416721.webp?size=96&quality=lossless"))
        self.set_footer(text=f'Active: {team.get("active")}')
        self.add_field(name='MMR', value=f'```{team.get("team_mmr")}```', inline=True)
        self.add_field(name='Captain', value=f'```{inter.user.name}```')



