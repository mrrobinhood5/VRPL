import discord
from pydantic import EmailStr, Field
from typing import Optional, Union
from classes.base import Base, PyObjectId
from config import DEFAULT_LOGO


class PlayerModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    discord_id: str  # figure out how to validate this
    game_uid: str  # figure out how to validate this
    calibrated_height: str
    promo_email: Optional[EmailStr]

    is_banned: bool = False
    is_suspended: bool = False
    player_mmr: int = 0

    class Config:
        schema_extra = {
            "example": {
                "name": "MrRobinhood5",
                "discord_id": "DISCORD_ID",
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


class PlayerEmbed(discord.Embed):

    def __init__(self, player: PlayerModel, user: discord.User):
        super().__init__(title=player.name, description=f'AKA {user.name}')
        self.color = discord.Color.orange()
        if user.avatar:
            self.set_thumbnail(url=user.avatar.url)
        else:
            self.set_thumbnail(url=DEFAULT_LOGO)
        self.set_footer(text=f'Banned: {player.is_banned} | Suspended: {player.is_suspended}')
        self.add_field(name='MMR', value=f'```{player.player_mmr}```')
        self.add_field(name='Game UID', value=f'```{player.game_uid}```')
        self.add_field(name='Calibrated Height', value=f'```{player.calibrated_height}```')


class PlayerUpdateModal(discord.ui.Modal, title='player update'):
    name = discord.ui.TextInput(label='Name', custom_id='name', placeholder='New Name', required=False)
    game_uid = discord.ui.TextInput(label='UID', custom_id='game_uid', placeholder='Updated UID', required=False)
    calibrated_height = discord.ui.TextInput(label='Calibrated Height', custom_id='calibrated_height',
                                             placeholder='New Height', required=False)
    promo_email = discord.ui.TextInput(label='Promo Email', custom_id='promo_email',
                                       placeholder='Email for Promos', required=False, )

    def __init__(self, view: discord.ui.View):
        super().__init__()
        self.view = view

    async def on_submit(self, inter: discord.Interaction) -> None:
        updated_player = {
            "name": self.name.value or None,
            "game_uid": self.game_uid.value or None,
            "calibrated_height": self.calibrated_height.value or None,
            "promo_email": self.promo_email.value or None
        }
        self.view.updated_player = updated_player
        await inter.response.send_message(f'Updates have been sent')
        self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)


class OwnPlayerView(discord.ui.View):

    def __init__(self, player: PlayerModel, user: discord.User):
        super().__init__()
        self.player = player
        self.user = user
        self.updated_player = None

    @discord.ui.button(label='Update', style=discord.ButtonStyle.blurple)
    async def update(self, inter: discord.Interaction, button: discord.ui.Button):
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

    def __init__(self, objects: Union[list[tuple[PlayerModel, discord.User]], None] = None):
        super().__init__()
        self.objects = objects
        self.obj_index = 0
        self.timeout = None
        self.updated_player = None

    @property
    def player_count(self):
        return len(self.objects)

    @property
    def next_player(self):
        self.obj_index = (self.obj_index + 1) % self.player_count
        yield self.objects[self.obj_index]

    @property
    def prev_player(self):
        self.obj_index = (self.obj_index - 1) % self.player_count
        yield self.objects[self.obj_index]

    @discord.ui.button(label='< Previous', style=discord.ButtonStyle.green)
    async def previous(self, inter: discord.Interaction, button: discord.ui.Button):
        player, user = next(self.prev_player)
        if inter.user.id == user.id:
            self.update.disabled = False
        else:
            self.update.disabled = True

        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(embed=PlayerEmbed(player, user), view=self)

    @discord.ui.button(label=f'1 of x', style=discord.ButtonStyle.grey)
    async def counter(self, inter: discord.Interaction, button: discord.ui.Button):
        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(view=self)

    @discord.ui.button(label='Update', style=discord.ButtonStyle.blurple, disabled=True)
    async def update(self, inter: discord.Interaction, button: discord.ui.Button):
        modal = PlayerUpdateModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        self.stop()

    @discord.ui.button(label='Next >', style=discord.ButtonStyle.green)
    async def next(self, inter: discord.Interaction, button: discord.ui.Button):
        player, user = next(self.next_player)
        if inter.user.id == user.id:
            self.update.disabled = False
        else:
            self.update.disabled = True

        self.counter.label = f'{self.obj_index + 1} of {self.player_count}'
        await inter.response.edit_message(embed=PlayerEmbed(player, user), view=self)
