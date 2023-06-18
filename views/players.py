from discord.ui import View, button, Button
from discord import ButtonStyle, Interaction

from fastapi.exceptions import HTTPException

from embeds.players import PlayerEmbed, PlayerRegisterEmbed
from models.players import PlayerModel, UpdatePlayerModel
from models.settings import SettingsModel
from modals.players import PlayerRegisterModal, PlayerUpdateModal
from routers.players import register_player
from routers.admin import set_settings
from models.errors import GenericErrorEmbed
from views.buttons import UpdateButton, CounterButton, ControlButton
from views.shared import Carousel

from typing import Optional


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

        channel = inter.channel.id
        try:
            await register_player(self.updated_player)
            self.updated_player.discord_user = inter.user
            await inter.client.get_channel(channel).send(content="**Player Registration**",
                                                         embed=PlayerEmbed(self.updated_player))

            # do the settings thing
            settings: SettingsModel = inter.client.server_config
            old_message = await inter.channel.fetch_message(settings.players_message)
            await old_message.delete()
            message = await inter.channel.send(embed=PlayerRegisterEmbed(), view=PlayerRegisterPersistent())
            settings.players_message = message.id
            await set_settings(settings)

        except HTTPException as e:
            await inter.client.get_channel(channel).send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)


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


class PlayerCarousel(Carousel):

    def __init__(self, items: Optional[list[PlayerModel]] = None):
        super().__init__(items=items, modal=PlayerRegisterModal(self))

    @staticmethod
    def is_mine(inter: Interaction, player: PlayerModel) -> bool:
        return str(inter.user.id) == player.discord_id

    async def update_view(self, inter: Interaction, item: PlayerModel):
        await inter.response.edit_message(embed=PlayerEmbed(item), view=self)
