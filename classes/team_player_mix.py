import discord
from discord.ui import View, button, Button
from discord import Interaction

from typing import Optional, Union

from classes.teams import TeamModel, TeamUpdateModal, UpdateTeamModel

from classes.players import PlayerModel

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


class FullTeamEmbed(discord.Embed):

    def __init__(self, team: FullTeamModel):
        super().__init__(title=team.name, description=team.team_motto)
        self.color = discord.Color.blurple()
        self.set_thumbnail(url=team.team_logo or DEFAULT_LOGO)
        self.set_footer(text=f'Active: {team.active}')
        self.add_field(name='MMR', value=f'```{team.team_mmr}```', inline=True)
        self.add_field(name='Captain', value=f'```{team.captain.name}```')
        self.add_field(name='CoCaptain', value=f'```{team.co_captain.name if team.co_captain else None}```')
        players = f''
        for player in team.members:
            players += f'`{player.name}`\n'
        self.add_field(name='Players', value=players)


class OwnTeamEmbed(FullTeamEmbed):

    def __init__(self, team: FullTeamModel):
        super().__init__(team=team)
        self.add_field(name='Warnings', value=f'```Warnings Here```')
        self.add_field(name='Infractions', value=f'```Infractions Here```')


class TeamCarousel(View):
    def __init__(self, teams: Union[list[FullTeamModel], None] = None):
        super().__init__()
        self.objects = teams
        self.obj_index = 0
        self.timeout = None
        self.updated_team = None

    @property
    def team(self) -> FullTeamModel:
        return self.objects[self.obj_index]

    def is_my_team(self, inter: Interaction, team: FullTeamModel) -> bool:
        if str(inter.user.id) == team.captain.discord_id:
            return True
        if team.co_captain:
            if str(inter.user.id) == team.co_captain.discord_id:
                return True
        return False

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
    async def previous(self, inter: Interaction, button: Button):
        if self.is_my_team(inter, team := next(self.prev_team)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(embed=FullTeamEmbed(team), view=self)

    @discord.ui.button(label=f'1 of ', style=discord.ButtonStyle.grey)
    async def counter(self, inter: Interaction, button: Button):
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(view=self)

    @discord.ui.button(label=f'Update', style=discord.ButtonStyle.blurple, disabled=True)
    async def update(self, inter: discord.Interaction, button: Button):
        modal = TeamUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @discord.ui.button(label='Next >', style=discord.ButtonStyle.green)
    async def next(self, inter: Interaction, button: Button):
        if self.is_my_team(inter, team := next(self.next_team)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(embed=FullTeamEmbed(team), view=self)

    @discord.ui.button(label='Request to Join', style=discord.ButtonStyle.red)
    async def join(self, inter: Interaction, button: Button):
        pass


class OwnTeamView(View):

    def __init__(self, team: FullTeamModel):
        super().__init__()
        self.team = team
        self.updated_team: Union[UpdateTeamModel, None] = None


    @discord.ui.button(label='Update', style=discord.ButtonStyle.blurple, )
    async def update(self, inter: Interaction, button: Button):
        modal = TeamUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @discord.ui.button(label='View Pending Joins', style=discord.ButtonStyle.green, disabled=True)
    async def approve_joins(self, inter: Interaction, button: Button):
        self.stop()

    @discord.ui.button(label='Remove Player', style=discord.ButtonStyle.danger, disabled=True)
    async def remove_player(self, inter: Interaction, button: Button):
        self.stop()

    @discord.ui.button(label='Co-Captain', style=discord.ButtonStyle.green, disabled=True)
    async def update_co_captain(self, inter: Interaction, button: Button):
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception, item) -> None:
        print(f'{error} called from the view')

    async def interaction_check(self, inter: Interaction) -> bool:
        _ = (self.team.captain.discord_id, self.team.co_captain.discord_id if self.team.co_captain else None)
        if str(inter.user.id) not in _:
            return False
        else:
            self.update_co_captain.disabled = False
            self.remove_player.disabled = False
            self.approve_joins.disabled = False
            self.update.disabled = False
            return True
