from pydantic import HttpUrl, Field
from classes.base import Base, PyObjectId

from typing import Optional, Union
from discord.ui import TextInput, Modal, Button, View
from discord import Embed, Interaction

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


class NewTeamEmbed(Embed):

    def __init__(self, inter: Interaction, team: dict):
        super().__init__(title=team['name'], description=team['team_motto'])
        self.color = discord.Color.blurple()
        self.set_thumbnail(url=team.get('team_logo', "https://cdn.discordapp.com/emojis/1058108114626416721.webp?size=96&quality=lossless"))
        self.set_footer(text=f'Active: {team.get("active")}')
        self.add_field(name='MMR', value=f'```{team.get("team_mmr")}```', inline=True)
        self.add_field(name='Captain', value=f'```{inter.user.name}```')


class TeamUpdateModal(Modal, title='Team Update'):
    name = TextInput(label='Name', custom_id='name', placeholder='New Name', required=False)
    motto = TextInput(label='Team Motto', custom_id='team_motto', placeholder='New Team Motto', required=False)
    logo = TextInput(label='Team Logo', custom_id='team_logo', placeholder='New Team Logo', required=False)

    def __init__(self, view: View) -> None:
        super().__init__()
        self.view = view

    async def on_submit(self, inter: Interaction) -> None:
        updated_team = {
            "name": self.name.value or None,
            "motto": self.motto.value or None,
            "logo": self.logo.value or None,
        }
        self.view.updated_team = updated_team
        await inter.response.send_message(f'Updates have been sent')
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception) -> None:
        await inter.response.send_message('Oops! Something went wrong', ephemeral=True)

