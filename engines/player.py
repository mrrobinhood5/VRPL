import pprint

from engines import *
from engines.base import BaseEngine
from engines.shared import *
from models import *
from pydantic import ValidationError
from typing import Type, TypeVar, Callable
from beanie.operators import RegEx, In, Eq, ElemMatch
from beanie import PydanticObjectId

B = TypeVar('B', bound=PlayerBase)
E = TypeVar('E', bound=BaseEngine)


class PlayerNames(BaseModel):
    name: str


class PlayerEngine(BaseEngine):
    base = PlayerBase

    @BaseEngine.embed_maker
    async def embed_maker(self,
                          embeds: Embeds,
                          item: Type[B] = None,
                          private: Optional[bool] = False) -> list[discord.Embed]:
        if not item:
            embed = embeds.public
            embed.title="Players Dashboard"
            embed.description="Options for managing League Players"
            return [embed]
        else:
            embed = embeds.public
            embed.title = item.name
            embed.description = f'`{item.game_uid}`'
            # thumbnail needs discord bot access
            # user = self.bot.get_user(item.discord_id)  # TODO: since its an async now, you can probably use fetch
            user = self.bot.get_user(item.discord_id)
            embed.set_thumbnail(url=user.display_avatar.url) if user else 0
            # all other fields
            embed.add_field(name='Registered Height', value=f'`{item.height}`', inline=True)
            embed.add_field(name='location', value=f'`{item.location}`', inline=True)
            embed.add_field(name='suspended', value=f'`{item.is_suspended}`', inline=True)
            embed.add_field(name='banned', value=f'`{item.is_banned}`')
            # Resolve the teams and games
            item.teams = await TeamBase.find(In(*ElemMatch('members', {}), [item.to_ref()]),
                                             with_children=True).to_list()
            for team in item.teams:
                team.game = await GameBase.get(team.game.ref.id, with_children=True)
            embed.add_field(name='teams', value=''.join([f'`{team.game.name} - {team.name}`' for team in item.teams]),
                            inline=True)
            embed.add_field(name='tournaments', value='`Not Implemented`')
            # embed.add_field(name='tournaments',
            #                 value=''.join([f'{tournament.name}' for tournament in item.tournaments]), inline=True)
            embed.add_field(name='Last Matches', value='xxx')
            embed.set_footer(text=f'Registered on VRPL on {item.registered_on}')

            if private:
                pembed = embeds.private  # TODO: make private embed of Player
                return [embed, pembed]
        return [embed]

    @BaseEngine.dashboard
    async def dashboard(self, /, dashboard: discord.ui.View, *args, **kwargs) -> discord.ui.View:
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(FindButton(engine=self, search_function=self.get_by))
         .add_item(CreateButton(engine=self, search_function=self.get_by))
         .add_item(UpdateButton())
         .add_item(DeleteButton()))
        return dashboard

    @BaseEngine.find_by_modal
    async def find_by_modal(self, /, modal: discord.ui.Modal) -> discord.ui.Modal:
        """ used to return a Modal Instance """
        items = [StandardInput(label='name', placeholder='Leave blank for ALL'),
                 StandardInput(label='location', placeholder='Leave blank for ALL'),
                 StandardInput(label='team', placeholder='Leave blank for ALL'),
                 StandardInput(label='captain', placeholder='yes or no or BLANK for ALL'),
                 StandardInput(label='banned', placeholder='yes or no or BLANK for ALL')]
        [modal.add_item(x) for x in items]
        return modal


    def user_picker(self, /, *args, **kwargs) -> discord.ui.View:
        view = discord.ui.View()
        select = UserSelect()
        view.add_item(select)
        return view

    @BaseEngine.create_modal
    async def create_modal(self, /,
                           modal: discord.ui.Modal,
                           inter: discord.Interaction) -> discord.ui.Modal:
        picker = self.user_picker()
        await inter.channel.send(content='', view=picker, delete_after=30)
        await picker.wait()
        print(picker.results)
        results=picker.results[0]
        items = [StandardInput(label='name', placeholder=f'{results.name}'), # TODO: make the user picker
                 StandardInput(label='game_uid', placeholder='Enter Game UID'),
                 StandardInput(label='height', placeholder='from 4.0 to 6.0'),
                 StandardInput(label='location', placeholder='Enter your country')]
        [modal.add_item(x) for x in items]
        return modal

    @BaseEngine.carousel
    async def carousel(self, /, carousel: CarouselView) -> CarouselView:
        """ Used to return a Carousel """
        (carousel.add_item(UpdateButton())
                 .add_item(DeleteButton()))
        return carousel

    # SEARCH Methods
    def get_by(self, *,
               name: Optional[str] = None,
               id: Optional[PydanticObjectId] = None,
               discord_member: Optional[int] = None,
               game: Optional[GameBase] = None,
               location: Optional[str] = None,
               banned: Optional[bool] = None,
               suspended: Optional[bool] = None,
               captain: Optional[Union[bool, str]] = None,
               co_captain: Optional[Union[bool, str]] = None,
               team: Optional[Union[TeamBase, str]] = None) -> Result:
        # dashboard searches is name, game, location, banned, captain,
        if captain:
            base = CaptainPlayer
        elif co_captain:
            base = CoCaptainPlayer
        else:
            base = PlayerEngine.base

        search = base.find({}, with_children=True)
        pipeline = []
        if id:
            search = search.find(Eq(base.id, id))
        if name:
            search = search.find(RegEx(base.name, name, 'i'))
        if discord_member:
            search = search.find(Eq(base.discord_id, discord_member))
        if game:  # Games is a list of Link
            search = search.aggregate(Pipeline()
                                      .lookup(right="GameBase", left_on='games.$id', right_on="_id", name='games')
                                      .match(**RegEx('games.name', game, 'i'))
                                      .export())
        if team:
            if isinstance(team, str):  # using the modal here

                pipeline = (Pipeline()
                            .lookup(right="TeamBase", left_on='_id', right_on='members.$id', name="teams")
                            .match(**ElemMatch('teams', **RegEx('name', team, 'i')))
                            .export())
                # search = search.find(ElemMatch(base.teams, RegEx(TeamBase.name, f'(?i){name}')))
            else:  # using the API here
                search = search.find(ElemMatch(base.teams, {'$in': [team]}))
        if location:
            # if you got a search phrase, parse it.
            search = search.find(RegEx(base.location, f'(?i){location}'))
            # search = search.find(Eq(base.location, location))
        if banned:
            search = search.find(Eq(base.is_banned, banned))
        if suspended is not None:
            search = search.find(Eq(base.is_suspended, True))

        return self.results_cursor(search.aggregate(pipeline, projection_model=PlayerBase))



    async def create_function(self, document: dict, **kwargs):
        base = NormalPlayer
        team = super().create_function(self, base=base, document=document)
        return team

    # NOTHING BELOW IS IMPLEMENTED
    @property
    async def settings(self) -> Optional[PlayerSettings]:
        return await PlayerSettings.find_all().first_or_none()

    async def all_player_locations(self, location: Optional[str] = None) -> list[AllPlayerLocations]:
        return await AllPlayerLocations.find(Eq(AllPlayerLocations.location, location) if location else {}).to_list()

    async def update_settings(self, message: discord.Message, channel: discord.TextChannel) -> PlayerSettings:
        if not await self.settings:
            settings = PlayerSettings(channel_id=channel.id, message_id=message.id)
            return await settings.insert()
        else:
            return await self.settings.set({'channel_id': channel.id, 'message_id': message.id})

    async def register_player(self, **kwargs) -> NormalPlayer:
        try:
            return await NormalPlayer(**kwargs).insert()
        except ValidationError as e:
            raise e

    async def make_captain(self, player: NormalPlayer) -> CaptainPlayer:
        """ This should only be called by the Team Engine, or Admin Engine  """
        try:
            # gotta get the games link
            player.games = [await Game.get(game.ref.id) for game in player.games]
            captain = CaptainPlayer(**player.dict())
            (await player.delete(), await captain.insert())
            return captain
        except ValidationError as e:
            raise e

    async def make_co_captain(self, player: Type[NormalPlayer]) -> CoCaptainPlayer:
        try:
            co_captain = CoCaptainPlayer(**dict(player), check_fields=False)
            (await player.delete(), await co_captain.insert())
            return co_captain
        except ValidationError as e:
            raise e

    # async def update(self, base: Type[B], updates: dict) -> Type[B]:
    #     try:
    #         return await base.set(updates)
    #     except ValidationError as e:
    #         raise e
