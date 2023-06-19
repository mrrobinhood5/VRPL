from typing import Optional, Literal

from discord import Interaction, ButtonStyle, Message, SelectOption
from discord.ui import View, button, Button, Select

from fastapi import HTTPException

from routers.admin import get_settings
from routers.teams import list_pending_approvals, update_team, show_team, remove_player

from models.players import PlayerTeamFullModel
from models.teamplayers import FullTeamModel
from models.teams import UpdateTeamModel
from models.settings import SettingsModel
from models.errors import GenericErrorEmbed

from views.buttons import UpdateButton
from views.approvals import TeamJoinsCarousel
from views.shared import Carousel

from modals.teams import TeamUpdateModal

from embeds.teamplayers import FullTeamEmbed
from embeds.players import PlayerEmbed


async def process_team_update(inter: Interaction, team_id: str, team: UpdateTeamModel):
    """ helper function to send updates of teams """
    try:
        await update_team(team_id, team)

        if settings := await get_settings():
            settings = SettingsModel(**settings)
            updated_team = FullTeamModel(**await show_team(str(team_id), full=True))
            await inter.client.get_channel(settings.teams_channel).send(content=f'', embed=FullTeamEmbed(updated_team))

    except HTTPException as e:
        await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))


class MemberChooseDropDown(Select):
    def __init__(self, options=list[SelectOption]):
        super().__init__(placeholder='Choose a Team Member', min_values=1, max_values=1, options=options)

    async def callback(self, inter: Interaction):
        self.view.chosen_value = self.values[0].split(':')
        await inter.response.send_message(f'`{inter.user.name}` has selected `{self.view.chosen_value[0]}`')
        if self.view.choose_type == 'co_captain':
            updated_team = UpdateTeamModel(**{'co_captain': self.view.chosen_value[1]})
            await process_team_update(inter, str(self.view.team.id), updated_team)
        else:
            try:
                await remove_player(self.view.chosen_value[1])
            except HTTPException as e:
                await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))
            else:
                if self.view.chosen_value[1] == str(self.view.team.co_captain.id):
                    updated_team = UpdateTeamModel(**{'co_captain': None})
                    await process_team_update(inter, str(self.view.team.id), updated_team)
        self.view.stop()


class MemberChooseView(View):
    def __init__(self, options: list[SelectOption], team: FullTeamModel, choose_type: Literal['co_captain', 'remove']):
        super().__init__()
        self.team = team
        self.choose_type = choose_type
        self.add_item(MemberChooseDropDown(options=options))
        self.chosen_value = None


class TeamCarousel(Carousel):
    def __init__(self, items: Optional[list[FullTeamModel]]):
        super().__init__(items=items, modal=TeamUpdateModal(self))

    @staticmethod
    def is_mine(inter: Interaction, team: FullTeamModel) -> bool:
        if str(inter.user.id) == team.captain.discord_id:
            return True
        if team.co_captain:
            if str(inter.user.id) == team.co_captain.discord_id:
                return True
        return False

    async def update_view(self, inter: Interaction, item: FullTeamModel):
        await inter.response.edit_message(embed=FullTeamEmbed(item), view=self)

    async def callback(self, inter: Interaction):
        await process_team_update(inter, str(self.item.id), self.updated_item) if self.updated_item else 0
        self.stop()


class OwnTeamView(View):

    def __init__(self, team: FullTeamModel):
        super().__init__()
        self.update = UpdateButton(TeamUpdateModal(view=self))
        self.add_item(self.update)
        self.team = team
        self.updated_team: Optional[UpdateTeamModel] = None
        self.msg_for_embed: Optional[Message] = None

    async def finish_off_view(self, inter: Interaction, view: View):
        await view.wait()
        view.clear_items()
        msg = await inter.original_response()
        await msg.edit(content=f'Updates Changed', view=view)
        self.stop()

    @button(label='View Pending Joins', style=ButtonStyle.green, disabled=False)
    async def approve_joins(self, inter: Interaction, button: Button):
        approvals = await list_pending_approvals(str(self.team.id), full=True)
        if approvals:
            approvals = [PlayerTeamFullModel(**approval) for approval in approvals]
            embed = PlayerEmbed(approvals[0].player)
            view = TeamJoinsCarousel(approvals)
            await inter.response.send_message(embed=embed, view=view, ephemeral=True)
            await view.wait()
        else:
            await inter.response.send_message(content=f'There are no pending Approvals', delete_after=10)
        self.stop()

    @button(label='Remove Player', style=ButtonStyle.danger, disabled=False)
    async def remove_player(self, inter: Interaction, button: Button):
        options = [SelectOption(label=member.name, value=f'{member.name}:{str(member.id)}')
                   for member in self.team.members if member.id != self.team.captain.id]
        view = MemberChooseView(options=options, team=self.team, choose_type='remove')
        await inter.response.send_message(content='Who do you want to remove', view=view, ephemeral=True)
        await self.finish_off_view(inter, view)

    @button(label='Co-Captain', style=ButtonStyle.green, disabled=False)
    async def update_co_captain(self, inter: Interaction, button: Button):
        if self.team.captain.discord_id != str(inter.user.id):
            inter.response.send_message(content='You are not Captain of this team :stop_sign:', ephemeral=True)
            self.stop()
        team_captains = [self.team.captain.id, self.team.co_captain.id if self.team.co_captain else None]
        options = [SelectOption(label=member.name, value=f'{member.name}:{str(member.id)}')
                   for member in self.team.members if member.id not in team_captains]
        view = MemberChooseView(options=options, team=self.team, choose_type='co_captain')
        await inter.response.send_message(content='Who do you choose as Co-Captain', view=view, ephemeral=True)
        await self.finish_off_view(inter, view)

    async def on_error(self, inter: Interaction, error: Exception, item) -> None:
        print(f'{error} called from the view')

    async def interaction_check(self, inter: Interaction) -> bool:
        _ = (self.team.captain.discord_id, self.team.co_captain.discord_id if self.team.co_captain else None)
        if str(inter.user.id) not in _:
            # TODO: this should error out if not cap / cocap
            return False
        else:
            return True

    async def callback(self, inter: Interaction):
        await process_team_update(inter, str(self.team.id), self.updated_team) if self.updated_team else 0
        self.stop()
