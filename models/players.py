# from email_validator import validate_email, EmailNotValidError
from views.shared import Carousel, ItemView, UpdateGenericModal
from bson.objectid import ObjectId
import discord
from pydantic import Field, confloat, validator
from config import DEFAULT_PLAYER_LOGO

from typing import Optional, Iterable
from pydantic_mongo import ObjectIdField, AbstractRepository
from database import DBConnect

from models.admin import Base




#
# PLAYER MODELS
#
class PlayerModel(Base):
    """ PlayerModel is the representation of a registered player in the league """
    id: ObjectIdField = None
    discord_id: int
    name: str
    game_uid: str  # TODO: can game uids be validated
    calibrated_height: confloat(gt=4.5, lt=6.5)  # TODO: validate within the parameters allowed
    promo_email: Optional[str]

    is_banned: bool = False
    is_suspended: bool = False
    mmr: int = 0

    discord_user: Optional[discord.User] = Field(default=None, exclude=True)

    @validator('discord_id')
    def check_discord_id(cls, v):
        """ Validates the id passed is a valid discord id """
        if user := cls._bot.get_user(v):
            return v
        else:
            raise ValueError('Not a Valid Discord User ID')

    @validator('discord_user', always=True)
    def check_discord_user(cls, v, values):
        """ if a discord user is passed, validates it, else grabs the current one """
        if v and isinstance(v, discord.User):
            return v
        else:
            return cls._bot.get_user(values.get('discord_id'))

    # @validator('promo_email') # TODO: Get the email validator working somehow
    # def check_email(cls, v):
    #     """ email validator """
    #     e = validate_email(v, check_deliverability=False)
    #     return e.normalized

    def public_embed(self) -> discord.Embed:
        """ Outputs the public embed for a player. It is displayed when other look at all players or when player
        updates happen """
        embed = discord.Embed(title=self.name, description=f'AKA {self.discord_user.name}',
                              color=discord.Color.orange())
        embed.set_thumbnail(url=self.discord_user.avatar.url if self.discord_user.avatar else DEFAULT_LOGO)
        embed.set_footer(text=f'Banned: {self.is_banned} | Suspended: {self.is_suspended}')
        embed.add_field(name='MMR', value=f'```{self.mmr}```')
        embed.add_field(name='Game UID', value=f'```{self.game_uid}```')
        embed.add_field(name='Calibrated Height', value=f'```{self.calibrated_height}```')
        return embed

    def private_embed(self) -> discord.Embed:
        """ Outputs a private embed for a player, when looking at it via the /players me command """
        embed = self.public_embed()
        embed.add_field(name='E-mail', value=f'```{self.promo_email}```')
        embed.add_field(name='Warnings', value=f'```List Warnings Here```')
        embed.add_field(name='Offences', value=f'```List Offences Here```')
        return embed

    @classmethod
    def db(cls):
        """ Returns a connection to a collection for this model """
        return PlayerRepo(DBConnect().db)
        # return cls._db

    @classmethod
    def get(cls, player: discord.Member) -> 'PlayerModel':
        """ retrieves a PlayerModel via a discord User """
        result = cls.db().find_one_by(query={'discord_id': player.id})
        if not result:
            raise ValueError("Player is not Registered")
        else:
            return result

    @classmethod
    def get_by_id(cls, player: ObjectIdField) -> 'PlayerModel':
        """ retrieves a PlayerModel from a ObjectID.
        Userful when grabbing PlayerModels from links in other collections """
        result = cls.db().find_one_by(query={'_id': player})
        if not result:
            raise ValueError("Player is not Registered")
        else:
            return result

    @classmethod
    def get_all(cls) -> Iterable['PlayerModel']:
        """ Returns a list of all PlayerModels in the collection for sorted from newest to oldest in creating date"""
        return list(cls.db().find_by(query={}, sort=[('_id', -1)]))

    @classmethod
    def get_some(cls, search: str) -> Iterable['PlayerModel']:
        """ Returns a list of all PlayerModels in the collection based on a search term for the name """
        results = cls.get_all()
        return [result for result in results if search in result.name]

    class PlayerView(ItemView):
        """ PlayerView returns a view for a single PlayerModel """

        def __init__(self, items: list['PlayerModel']):
            self.modal = PlayerUpdateModal(view=self)
            super().__init__(items=items, modal=self.modal)

        async def interaction_check(self, inter: discord.Interaction) -> bool:
            return inter.user == self.item.discord_user

        async def callback(self, inter: discord.Interaction):
            """ Callback for when the Update Button is pressed """
            result = self.updated_item.save()
            await inter.edit_original_response(
                content=f'{"Success" if result.acknowledged else "Error!"}', embed=None, view=None)
            if result.acknowledged:
                self.updated_item = PlayerModel.get(inter.user)  # You need to get the updated version from the DB
                await inter.channel.send(content='**Player Update**', embed=self.updated_item.public_embed())
            self.stop()

    class PlayerCarousel(Carousel):
        """ Returns a Carousel View for a list of passed PlayerModels """

        def __init__(self, items: Optional[Iterable['PlayerModel']]):
            self.modal = PlayerUpdateModal(view=self)
            super().__init__(items=items, modal=self.modal)

        @staticmethod
        def is_mine(inter: discord.Interaction, player: 'PlayerModel') -> bool:
            return inter.user == player.discord_user

        async def callback(self, inter: discord.Interaction):
            """ Callback for when the Update Button is pressed """
            result = self.updated_item.save()
            await inter.edit_original_response(
                content=f'{"Success" if result.acknowledged else "Error!"}', embed=None, view=None)
            if result.acknowledged:
                self.updated_item = PlayerModel.get(inter.user)  # You need to get the updated version from the DB
                await inter.channel.send(content='**Player Update**', embed=self.updated_item.public_embed())
            self.stop()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {}


class PlayerRepo(AbstractRepository[PlayerModel]):
    """ Allows PlayerModles to update themselves in the db collection """

    class Meta:
        collection_name = 'players'


#
# PLAYER MODALS
#
class PlayerRegisterModal(UpdateGenericModal, title='Register a Player'):
    """ Form used to register players """
    game_uid = discord.ui.TextInput(label='UID', custom_id='game_uid', placeholder='Updated UID', required=True)
    calibrated_height = discord.ui.TextInput(label='Calibrated Height', custom_id='calibrated_height',
                                             placeholder='New Height', required=True)
    promo_email = discord.ui.TextInput(label='Promo Email', custom_id='promo_email',
                                       placeholder='Email for Promos (Optional)', required=False, default=None)

    def __init__(self, view: discord.ui.View):
        super().__init__(view=view)

    async def on_submit(self, inter: discord.Interaction) -> None:
        """ Called when the form is submitted """
        item = PlayerModel(name=inter.user.name,
                           discord_id=inter.user.id,
                           game_uid=self.game_uid.value,
                           calibrated_height=self.calibrated_height.value,
                           promo_email=self.promo_email.value or None)
        self.view.updated_item = item
        result = item.save()
        await inter.response.send_message(f'{"Success" if result.acknowledged else "Error!!"}', ephemeral=True)
        self.stop()


class PlayerUpdateModal(PlayerRegisterModal, title='Player update'):
    """ Form used to update Players """
    name = discord.ui.TextInput(label='Name', custom_id='name', placeholder='New Name', required=False)

    def __init__(self, view: discord.ui.View):
        super().__init__(view=view)
        for text_input in self.children:
            text_input.required = False

    async def on_submit(self, inter: discord.Interaction) -> None:
        """ Called when Submitting the Form. Adds updates to the PlayerModel and updates itself to the DB"""
        updates = {x.custom_id: x.value for x in self.children if x.value}
        self.view.updated_item = self.view.item.copy(update=updates, deep=True) if updates else None
        await inter.response.send_message(f'Updates have been sent', delete_after=10)


#
# PERSISTENT VIEWS
#
class PlayerRegisterPersistent(discord.ui.View):
    """ This is the View that will be used for Player Registrations """

    def __init__(self):
        super().__init__(timeout=None)
        self.updated_player: Optional[PlayerModel] = None

    @discord.ui.button(label='Register a Player', style=discord.ButtonStyle.green, custom_id='player:register')
    async def register(self, inter: discord.Interaction, button: discord.Button):
        if player := PlayerModel.get(inter.user):
            await inter.response.send_message('You are already Registered!', ephemeral=True)
            return

        modal = PlayerRegisterModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()
        await inter.channel.send(content="**Player Registration**", embed=self.updated_player.public_embed())

    def embed(self) -> discord.Embed:
        embed = discord.Embed(title="Player Registration", description="Click below to register a player")
        embed.add_field(name='Registrations',
                        value=f'By registering a player, you are agreeing to the VRPL code of conduct and rules')
        embed.add_field(name='Game UID', value=f'You can find the game UID from the options menu. Please have it ready')
        embed.add_field(name='Calibrated Height',
                        value=f'Please list the height you will be using in this league. You can update it later, '
                              f'but we track all edits to prevent abuse')
        embed.add_field(name='Optionals', value=f'Providing your email is optional, and not required to participate')
        embed.set_image(url='https://i.imgur.com/34eBdG2.png')
        embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
        return embed
