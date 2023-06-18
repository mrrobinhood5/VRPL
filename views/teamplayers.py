from discord.ui import View, button, Button, Modal
from discord import Interaction, ButtonStyle, Message
from typing import Optional

from models.players import PlayerTeamModel, PlayerModel
from models.teamplayers import FullTeamModel
from modals.teams import TeamUpdateModal
from models.teams import UpdateTeamModel
from embeds.teamplayers import FullTeamEmbed
from embeds.players import PlayerEmbed
from views.buttons import UpdateButton, CounterButton
from views.approvals import TeamJoinsCarousel
from views.shared import Carousel

from routers.teams import list_pending_approvals
from routers.players import show_player


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
        # then build the view
        approvals = await list_pending_approvals(str(self.team.id))
        players = [PlayerModel(**await show_player(str(approval.get('player')))) for approval in approvals]
        embed = PlayerEmbed(players[0])
        view = TeamJoinsCarousel(players)
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
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
