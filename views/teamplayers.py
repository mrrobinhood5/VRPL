from discord.ui import View, button, Button
from discord import Interaction, ButtonStyle, Message
from typing import Optional

from fastapi import HTTPException

from models.players import PlayerModel, PlayerTeamFullModel
from models.teamplayers import FullTeamModel
from modals.teams import TeamUpdateModal
from models.teams import UpdateTeamModel
from embeds.teamplayers import FullTeamEmbed
from embeds.players import PlayerEmbed
from models.errors import GenericErrorEmbed
from views.buttons import UpdateButton
from views.approvals import TeamJoinsCarousel
from views.shared import Carousel

from routers.teams import list_pending_approvals, update_team, show_team



async def process_team_update(inter: Interaction, team_id: str, team: UpdateTeamModel):
    """ helper function to send updates of teams """
    try:
        await update_team(team_id, team)
        if _ := inter.client.server_config.teams_channel:
            updated_team = FullTeamModel(**await show_team(str(team_id), full=True))
            await inter.client.get_channel(_).send(content=f'', embed=FullTeamEmbed(updated_team))

    except HTTPException as e:
        await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))


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
        self.stop()

    @button(label='Co-Captain', style=ButtonStyle.green, disabled=False)
    async def update_co_captain(self, inter: Interaction, button: Button):
        self.stop()

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
