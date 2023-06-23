from typing import Optional

from fastapi.exceptions import HTTPException

from discord import ButtonStyle, Interaction
from discord.ui import View, button, Button

from routers.players import register_player, update_player, show_player
from routers.admin import get_settings

from views.buttons import UpdateButton
from views.shared import Carousel

from models.players import PlayerModel, UpdatePlayerModel
from models.settings import SettingsModel
from models.errors import GenericErrorEmbed

from embeds.players import PlayerEmbed

from modals.players import PlayerRegisterModal, PlayerUpdateModal


async def process_player_update(inter: Interaction, player: UpdatePlayerModel):
    """ Helper function to process any player updates """
    try:
        await update_player(str(inter.user.id), player)

        if settings := await get_settings():
            settings = SettingsModel(**settings)
            updated_player = PlayerModel(**await show_player(str(inter.user.id)))
            updated_player.discord_user = inter.user
            await inter.client.get_channel(settings.players_channel).send(content=f'**Player Update**',
                                                                          embed=PlayerEmbed(updated_player))

    except HTTPException as e:
        await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))


class PlayerRegisterPersistent(View):
    """ This is the View that will be used for Player Registrations """
    def __init__(self):
        super().__init__(timeout=None)
        self.updated_player: Optional[PlayerModel] = None

    @button(label='Register a Player', style=ButtonStyle.green, custom_id='player:register')
    async def register(self, inter: Interaction, button: Button):
        modal = PlayerRegisterModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()

        try:
            await register_player(self.updated_player)
            self.updated_player.discord_user = inter.user
            await inter.channel.send(content="**Player Registration**", embed=PlayerEmbed(self.updated_player))
        except HTTPException as e:
            await inter.client.channel.send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)


class OwnPlayerView(View):

    def __init__(self, player: PlayerModel):
        super().__init__()
        self.update = UpdateButton(PlayerUpdateModal(view=self))
        self.add_item(self.update)

        self.player = player
        self.user = player.discord_user
        self.updated_player: Optional[UpdatePlayerModel] = None

    async def on_error(self, inter: Interaction, error: Exception, item) -> None:
        print(f'{error} called from the view')

    async def interaction_check(self, inter: Interaction) -> bool:
        if self.user.id != inter.user.id:
            return False
        else:
            return True

    async def callback(self, inter: Interaction):
        await process_player_update(inter, self.updated_player) if self.updated_player else 0
        self.stop()


class PlayerCarousel(Carousel):

    def __init__(self, items: Optional[list[PlayerModel]] = None):
        super().__init__(items=items, modal=PlayerUpdateModal(self))

    @staticmethod
    def is_mine(inter: Interaction, player: PlayerModel) -> bool:
        return str(inter.user.id) == player.discord_id

    async def update_view(self, inter: Interaction, item: PlayerModel):
        await inter.response.edit_message(embed=PlayerEmbed(item), view=self)

    async def callback(self, inter: Interaction):
        await process_player_update(inter, self.updated_player) if self.updated_player else 0
        self.stop()
