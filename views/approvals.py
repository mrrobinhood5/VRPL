from models.players import PlayerModel
from typing import Optional
from discord import Interaction
from views.shared import Carousel
from embeds.players import PlayerEmbed
from views.buttons import ApproveButton, RejectButton


class TeamJoinsCarousel(Carousel):
    def __init__(self, items: Optional[list[PlayerModel]]):
        super().__init__(items=items, modal=None)
        self.remove_item(self.update)
        self.add_item(ApproveButton()).add_item(RejectButton())

    @staticmethod
    def is_mine(inter: Interaction, item: PlayerModel):
        return True

    async def update_view(self, inter: Interaction, item:PlayerModel):
        await inter.response.edit_message(embed=PlayerEmbed(item), view=self)