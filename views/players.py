from discord.ui import View, button, Button
from discord import ButtonStyle, Interaction

from fastapi.exceptions import HTTPException

from embeds.players import PlayerEmbed
from models.players import PlayerModel, UpdatePlayerModel
from modals.players import PlayerRegisterModal, PlayerUpdateModal
from routers.players import register_player
from models.errors import GenericErrorEmbed

from typing import Optional


class PlayerRegisterPersistent(View):
    """ This is the View that will be used for Player Registrations """
    def __init__(self):
        super().__init__(timeout=None)
        self.updated_player: PlayerModel = None

    @button(label='Register a Player', style=ButtonStyle.green, custom_id='player:register')
    async def register(self, inter: Interaction, button: Button):
        modal = PlayerRegisterModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()

        channel = inter.channel.id
        try:
            await register_player(self.updated_player)
            self.updated_player.discord_user = inter.user
            await inter.client.get_channel(channel).send(content="**Player Registration**", embed=PlayerEmbed(self.updated_player))
        except HTTPException as e:
            await inter.client.get_channel(channel).send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)


class OwnPlayerView(View):

    def __init__(self, player: PlayerModel):
        super().__init__()
        self.player = player
        self.user = player.discord_user
        self.updated_player: Optional[UpdatePlayerModel] = None

    @button(label='Update', style=ButtonStyle.blurple)
    async def update(self, inter: Interaction, button: Button):
        modal = PlayerUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception, item) -> None:
        print(f'{error} called from the view')

    async def interaction_check(self, inter: Interaction) -> bool:
        if self.user.id != inter.user.id:
            return False
        else:
            return True


class PlayerCarousel(View):

    def __init__(self, players: Optional[list[PlayerModel]] = None):
        super().__init__()
        self.players = players
        self.obj_index = 0
        self.timeout = None
        self.updated_player = None

    def is_me(self, inter: Interaction, player: PlayerModel) -> bool:
        return inter.user.id == player.discord_user.id

    @property
    def player_count(self):
        return len(self.players)

    @property
    def next_player(self):
        self.obj_index = (self.obj_index + 1) % self.player_count
        yield self.players[self.obj_index]

    @property
    def prev_player(self):
        self.obj_index = (self.obj_index - 1) % self.player_count
        yield self.players[self.obj_index]

    @button(label='< Previous', style=ButtonStyle.green)
    async def previous(self, inter: Interaction, button: Button):
        if self.is_me(inter, player := next(self.prev_player)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(embed=PlayerEmbed(player), view=self)

    @button(label=f'1 of x', style=ButtonStyle.grey)
    async def counter(self, inter: Interaction, button: Button):
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(view=self)

    @button(label='Update', style=ButtonStyle.blurple, disabled=True)
    async def update(self, inter: Interaction, button: Button):
        modal = PlayerUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @button(label='Next >', style=ButtonStyle.green)
    async def next(self, inter: Interaction, button: Button):
        if self.is_me(inter, player := next(self.next_player)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(embed=PlayerEmbed(player), view=self)