import discord
from pydantic import EmailStr, Field
from typing import Optional, Union, Any
from classes.base import Base, PyObjectId
from config import DEFAULT_LOGO
from discord import Interaction, ButtonStyle, Embed
from discord.ui import Button, View, Modal


class PlayerModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    discord_id: str
    game_uid: str
    calibrated_height: str
    promo_email: Optional[EmailStr]

    is_banned: bool = False
    is_suspended: bool = False
    player_mmr: int = 0

    discord_user: Optional[Any]

    class Config:
        schema_extra = {
            "example": {
                "name": "MrRobinhood5",
                "discord_id": "abc123456789",
                "game_uid": "1234567890",
                "calibrated_height": "5ft 6in",
            }
        }


class UpdatePlayerModel(Base):
    name: Optional[str]
    promo_email: Optional[EmailStr]
    game_uid: Optional[str]
    calibrated_height: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "New In Game Name",
                "promo_email": "myemail@mydomain.com",
                "game_uid": "1234567890",
                "calibrated_height": "5ft 6in"
            }
        }


class PlayerTeamModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    player: PyObjectId
    name: Optional[str]
    team: Optional[PyObjectId]
    approved: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "team": "ObjectId",
                "player": "ObjectId"
            }
        }


class UpdatePlayerTeamModel(Base):
    name: Optional[str]
    approved: bool

    class Config:
        schema_extra = {
            "example": {
                "approved": True
            }
        }


class PlayerEmbed(Embed):

    def __init__(self, player: PlayerModel):
        super().__init__(title=player.name, description=f'AKA {player.discord_user.name}')
        self.color = discord.Color.orange()
        if player.discord_user.avatar:
            self.set_thumbnail(url=player.discord_user.avatar.url)
        else:
            self.set_thumbnail(url=DEFAULT_LOGO)
        self.set_footer(text=f'Banned: {player.is_banned} | Suspended: {player.is_suspended}')
        self.add_field(name='MMR', value=f'```{player.player_mmr}```')
        self.add_field(name='Game UID', value=f'```{player.game_uid}```')
        self.add_field(name='Calibrated Height', value=f'```{player.calibrated_height}```')


class SelfPlayerEmbed(PlayerEmbed):

    def __init__(self, player: PlayerModel):
        super().__init__(player=player)
        self.add_field(name='E-mail', value=f'```{player.promo_email}```')
        self.add_field(name='Warnings', value=f'```List Warnings Here```')
        self.add_field(name='Offences', value=f'```List Offences Here```')


class PlayerRegisterModal(Modal, title='Register a Player'):
    game_uid = discord.ui.TextInput(label='UID', custom_id='game_uid', placeholder='Updated UID', required=True)
    calibrated_height = discord.ui.TextInput(label='Calibrated Height', custom_id='calibrated_height',
                                             placeholder='New Height', required=True)
    promo_email = discord.ui.TextInput(label='Promo Email', custom_id='promo_email',
                                       placeholder='Email for Promos (Optional)', required=False, default=None)

    def __init__(self, view: View):
        super().__init__()
        self.view = view

    async def on_submit(self, inter: Interaction) -> None:
        new_player = {
            "name": inter.user.name,
            "discord_id": str(inter.user.id),
            "game_uid": self.game_uid.value,
            "calibrated_height": self.calibrated_height.value,
            "promo_email": self.promo_email.value or None
        }
        self.view.updated_player = PlayerModel(**new_player)
        await inter.response.send_message(f'Registration Sent!', ephemeral=True)
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception) -> None:
        await inter.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)

class PlayerUpdateModal(Modal, title='Player update'):
    name = discord.ui.TextInput(label='Name', custom_id='name', placeholder='New Name', required=False)
    game_uid = discord.ui.TextInput(label='UID', custom_id='game_uid', placeholder='Updated UID', required=False)
    calibrated_height = discord.ui.TextInput(label='Calibrated Height', custom_id='calibrated_height',
                                             placeholder='New Height', required=False)
    promo_email = discord.ui.TextInput(label='Promo Email', custom_id='promo_email',
                                       placeholder='Email for Promos', required=False, )

    def __init__(self, view: View):
        super().__init__()
        self.view = view

    async def on_submit(self, inter: Interaction) -> None:
        updated_player = {
            "name": self.name.value or None,
            "game_uid": self.game_uid.value or None,
            "calibrated_height": self.calibrated_height.value or None,
            "promo_email": self.promo_email.value or None
        }
        self.view.updated_player = UpdatePlayerModel(**updated_player)
        await inter.response.send_message(f'Updates have been sent')
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception) -> None:
        await inter.response.send_message('Oops! Something went wrong.', ephemeral=True)


class OwnPlayerView(discord.ui.View):

    def __init__(self, player: PlayerModel):
        super().__init__()
        self.player = player
        self.user = player.discord_user
        self.updated_player: Optional[UpdatePlayerModel] = None

    @discord.ui.button(label='Update', style=discord.ButtonStyle.blurple)
    async def update(self, inter: Interaction, button: discord.ui.Button):
        modal = PlayerUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception, item) -> None:
        print(f'{error} called from the view')

    async def interaction_check(self, inter: discord.Interaction) -> bool:
        if self.user.id != inter.user.id:
            return False
        else:
            return True


class PlayerCarousel(discord.ui.View):

    def __init__(self, players: Union[list[PlayerModel], None] = None):
        super().__init__()
        self.players = players
        self.obj_index = 0
        self.timeout = None
        self.updated_player = None

    def is_me(self, inter: discord.Interaction, player: PlayerModel) -> bool:
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

    @discord.ui.button(label='< Previous', style=discord.ButtonStyle.green)
    async def previous(self, inter: Interaction, button: Button):
        if self.is_me(inter, player := next(self.prev_player)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(embed=PlayerEmbed(player), view=self)

    @discord.ui.button(label=f'1 of x', style=ButtonStyle.grey)
    async def counter(self, inter: Interaction, button: Button):
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(view=self)

    @discord.ui.button(label='Update', style=ButtonStyle.blurple, disabled=True)
    async def update(self, inter: Interaction, button: Button):
        modal = PlayerUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @discord.ui.button(label='Next >', style=ButtonStyle.green)
    async def next(self, inter: Interaction, button: Button):
        if self.is_me(inter, player := next(self.next_player)):
            self.update.disabled = False
        else:
            self.update.disabled = True
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(embed=PlayerEmbed(player), view=self)


class PlayerRegisterEmbed(Embed):
    def __init__(self):
        super().__init__(title="Player Registration", description="Click below to register a player")
        self.add_field(name='Registrations', value=f'By registering a player, you are agreeing to the VRPL code of '
                                                   f'conduct and rules')
        self.add_field(name='Game UID', value=f'You can find the game UID from the options menu. Please have it ready.')
        self.add_field(name='Calibrated Height', value=f'Please list the height you will be using in this league. '
                                                       f'You can update it later, but we track all edits to prevent abuse')
        self.add_field(name='Optionals', value=f'Providing your email is optional, and not required to participate')
        self.set_image(url='https://i.imgur.com/34eBdG2.png')
        self.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
