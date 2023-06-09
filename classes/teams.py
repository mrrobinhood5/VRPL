from pydantic import HttpUrl, Field
from classes.base import Base, PyObjectId
from classes.players import PlayerModel


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



# TODO inherit both TeamRegisterModal and PlayerRegisterModal
class TeamRegisterModal(Modal, title='Register a Team'):
    team_name = discord.ui.TextInput(label='Team Name', custom_id='name', placeholder='New Team Name', required=True)
    team_motto = discord.ui.TextInput(label='Team Motto', custom_id='team_motto', placeholder='Team Motto', required=True)
    team_logo = discord.ui.TextInput(label='Team Logo URL', custom_id='team_logo', placeholder='URL for Team Image', required=False, default=None)

    def __init__(self, view: View, captain: PlayerModel):
        super().__init__()
        self.view = view
        self.captain = captain

    async def on_submit(self, inter: Interaction) -> None:
        new_team = {
            "name": self.team_name.value,
            "team_motto": self.team_motto.value,
            "team_logo": self.team_logo.value or None,
            "captain": str(self.captain.id)
        }
        self.view.updated_team = TeamModel(**new_team)
        await inter.response.send_message(f'Registration Sent!', ephemeral=True)
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception) -> None:
        await inter.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)

class TeamRegisterEmbed(Embed):
    def __init__(self):
        super().__init__(title="Team Registration", description="Click below to register a team")
        self.add_field(name='Registrations', value=f'By registering a team, you are opening up sign-ups for your team. Only a Captain / Co-Captain can approved the team join requests')
        self.add_field(name='Team Name', value=f'You will be submitting the proper name for your team')
        self.add_field(name='Team Motto', value=f'This will be the text used to describe your team. ')
        self.add_field(name='Team Logo', value=f'You can use an imgur link or a discord link to provide the team URL')
        self.set_image(url='https://i.imgur.com/34eBdG2.png')
        self.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')

