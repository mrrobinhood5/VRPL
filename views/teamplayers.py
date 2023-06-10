from discord.ui import View, button, Button
from discord import Interaction, ButtonStyle
from typing import Optional

from models.teamplayers import FullTeamModel
from modals.teams import TeamUpdateModal
from models.teams import UpdateTeamModel
from embeds.teamplayers import FullTeamEmbed


class TeamCarousel(View):
    def __init__(self, teams: Optional[list[FullTeamModel]] = None):
        super().__init__()
        self.objects = teams
        self.obj_index = 0
        self.timeout = None
        self.updated_team = None

    @property
    def team(self) -> FullTeamModel:
        return self.objects[self.obj_index]

    @staticmethod
    def is_my_team(inter: Interaction, team: FullTeamModel) -> bool:
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

    @button(label='< Previous', style=ButtonStyle.green)
    async def previous(self, inter: Interaction, button: Button):
        if self.is_my_team(inter, team := next(self.prev_team)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(embed=FullTeamEmbed(team), view=self)

    @button(label=f'1 of ', style=ButtonStyle.grey)
    async def counter(self, inter: Interaction, button: Button):
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(view=self)

    @button(label=f'Update', style=ButtonStyle.blurple, disabled=True)
    async def update(self, inter: Interaction, button: Button):
        modal = TeamUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @button(label='Next >', style=ButtonStyle.green)
    async def next(self, inter: Interaction, button: Button):
        if self.is_my_team(inter, team := next(self.next_team)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.team_count}'
        await inter.response.edit_message(embed=FullTeamEmbed(team), view=self)

    @button(label='Request to Join', style=ButtonStyle.red)
    async def join(self, inter: Interaction, button: Button):
        pass


class OwnTeamView(View):

    def __init__(self, team: FullTeamModel):
        super().__init__()
        self.team = team
        self.updated_team: Optional[UpdateTeamModel] = None

    @button(label='Update', style=ButtonStyle.blurple, )
    async def update(self, inter: Interaction, button: Button):
        modal = TeamUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @button(label='View Pending Joins', style=ButtonStyle.green, disabled=True)
    async def approve_joins(self, inter: Interaction, button: Button):
        self.stop()

    @button(label='Remove Player', style=ButtonStyle.danger, disabled=True)
    async def remove_player(self, inter: Interaction, button: Button):
        self.stop()

    @button(label='Co-Captain', style=ButtonStyle.green, disabled=True)
    async def update_co_captain(self, inter: Interaction, button: Button):
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception, item) -> None:
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
