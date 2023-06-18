from models.players import PlayerModel
from typing import Optional
from discord import Interaction
from views.shared import Carousel
from embeds.players import PlayerEmbed
from views.buttons import ApproveButton, RejectButton
from routers.teams import approve_team_join, show_team
from models.players import PlayerTeamFullModel, UpdatePlayerTeamModel
from models.teamplayers import FullTeamModel
from embeds.teamplayers import FullTeamEmbed
from fastapi import HTTPException
from models.errors import GenericErrorEmbed


class TeamJoinsCarousel(Carousel):
    def __init__(self, items: Optional[list[PlayerTeamFullModel]]):
        super().__init__(items=items, modal=None)
        self.remove_item(self.update)
        self.add_item(ApproveButton()).add_item(RejectButton())
        self.approval = None

    @staticmethod
    def is_mine(inter: Interaction, item: PlayerModel):
        return True

    async def update_view(self, inter: Interaction, item:PlayerTeamFullModel):
        await inter.response.edit_message(embed=PlayerEmbed(item.player), view=self)

    async def callback(self, inter: Interaction):
        if self.approval:
            try:
                _ = UpdatePlayerTeamModel(**{'approved': True})
                await approve_team_join(approval_id=str(self.item.id), request=_)
                if _ := inter.client.server_config.teams_channel:
                    updated_team = FullTeamModel(**await show_team(str(self.item.team.id), full=True))
                    await inter.client.get_channel(_).send(content=f'', embed=FullTeamEmbed(updated_team))
            except HTTPException as e:
                await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))
        self.stop()
