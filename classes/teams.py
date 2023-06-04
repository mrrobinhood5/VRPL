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


class FullTeamEmbed(discord.Embed):

    def __init__(self, inter: discord.Interaction, team: dict):
        super().__init__(title=team['name'], description=team['team_motto'])
        self.color = discord.Color.blurple()
        self.set_thumbnail(url=team['team_logo'])
        self.set_footer(text=f'Active: {team["active"]}')
        self.add_field(name='MMR', value=f'```{team["team_mmr"]}```', inline=True)
        self.add_field(name='Captain', value=f'```{team["captain"]["name"]}```')

        self.add_field(name='CoCaptain', value=f'```{team["co_captain"]["name"]}```')
        players = [player['name'] for player in team['players']]
        self.add_field(name='Players', value=f'```{players} ```')

class NewTeamEmbed(discord.Embed):

    def __init__(self, inter: discord.Interaction, team: dict):
        super().__init__(title=team['name'], description=team['team_motto'])
        self.color = discord.Color.blurple()
        self.set_thumbnail(url=team.get('team_logo', "https://cdn.discordapp.com/emojis/1058108114626416721.webp?size=96&quality=lossless"))
        self.set_footer(text=f'Active: {team.get("active")}')
        self.add_field(name='MMR', value=f'```{team.get("team_mmr")}```', inline=True)
        self.add_field(name='Captain', value=f'```{inter.user.name}```')


class TeamCarousel(discord.ui.View):
    def __init__(self, objects: Union[list, None] = None):
        super().__init__()
        self.objects = objects
        self.obj_index = 0
        self.timeout = None

    @property
    def team_count(self):
        return len(self.objects)

    @property
    def next_team(self):
        self.obj_index = (self.obj_index + 1) % self.team_count
        yield self.objects[self.obj_index]

    @property
    def prev_team(self):
        self.obj_index = (self.obj_index - 1) % self.team_count
        yield self.objects[self.obj_index]

    @discord.ui.button(label='< Previous', style=discord.ButtonStyle.green)
    async def previous(self, inter: discord.Interaction, button: discord.ui.Button):
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(embed=FullTeamEmbed(inter, next(self.prev_team)), view=self)

    @discord.ui.button(label=f'1 of ', style=discord.ButtonStyle.grey)
    async def counter(self, inter: discord.Interaction, button: discord.ui.Button):
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(view=self)

    @discord.ui.button(label='Next >', style=discord.ButtonStyle.green)
    async def next(self, inter: discord.Interaction, button: discord.ui.Button):
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(embed=FullTeamEmbed(inter, next(self.next_team)), view=self)

    @discord.ui.button(label='Request to Join', style=discord.ButtonStyle.red)
    async def join(self, inter: discord.Interaction, button: discord.ui.Button):
        pass
