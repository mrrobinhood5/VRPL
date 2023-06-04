from pydantic import HttpUrl, Field
from typing import Optional, Union
from classes.base import Base, PyObjectId
from classes.teams import TeamModel
from classes.players import PlayerModel
import discord
from config import DEFAULT_LOGO


class FullTeamModel(TeamModel):
    captain: PlayerModel
    co_captain: Optional[PlayerModel]
    members: list[PlayerModel]

    class Config:
        schema_extra = {
            "example": {
                "_id": "abc123456789",
                "team_motto": "We are Great!",
                "team_logo": "http://logos.com/img.jpg",
                "active": True,
                "team_mmr": 0,
                "captain": {
                    "_id": "abc123456789",
                    "name": "captain name",
                    "discord_id": "987654321",
                    "game_uid": "uiduiduiduid",
                    "calibrated_height": "72 in"
                },
                "co_captain": {
                    "_id": "abc123456789",
                    "name": "captain name",
                    "discord_id": "987654321",
                    "game_uid": "uiduiduiduid",
                    "calibrated_height": "72 in"
                },
                "members": [
                    {
                        "_id": "abc123456789",
                        "name": "captain name",
                        "discord_id": "987654321",
                        "game_uid": "uiduiduiduid",
                        "calibrated_height": "72 in"
                    },
                    {
                        "_id": "abc123456789",
                        "name": "captain name",
                        "discord_id": "987654321",
                        "game_uid": "uiduiduiduid",
                        "calibrated_height": "72 in"
                    }
                ]

            }
        }

# TODO: Rework the Full Team Embed
class FullTeamEmbed(discord.Embed):

    def __init__(self, inter: discord.Interaction, team: FullTeamModel):
        super().__init__(title=team.name, description=team.team_motto)
        self.color = discord.Color.blurple()
        self.set_thumbnail(url=team.team_logo or DEFAULT_LOGO)
        self.set_footer(text=f'Active: {team.active}')
        self.add_field(name='MMR', value=f'```{team.team_mmr}```', inline=True)
        self.add_field(name='Captain', value=f'```{team.captain.name}```')

        self.add_field(name='CoCaptain', value=f'```{team.co_captain.name}```')
        players = [player.name for player in team.members]
        self.add_field(name='Players', value=f'```{players} ```')


class TeamCarousel(discord.ui.View):
    def __init__(self, objects: Union[list[FullTeamModel], None] = None):
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