from engines import *
from engines.base import BaseEngine
from engines.shared import *
from models import *
from pydantic import ValidationError
from typing import Type, TypeVar, Callable
from beanie.operators import RegEx, In, Eq, ElemMatch

B = TypeVar('B', bound=PlayerBase)
E = TypeVar('E', bound=BaseEngine)


class PlayerNames(BaseModel):
    name: str


class PlayerEngine(BaseEngine):
    base = PlayerBase

    async def embed_maker(self, item: Type[B] = None, private: Optional[bool] = False) -> list[discord.Embed]:

        if not item:
            embed = discord.Embed(title="Players Dashboard", description="Options for managing League Players")
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
        else:
            embed = discord.Embed(title=item.name, description=item.game_uid)
            # thumbnail needs discord bot access
            # user = self.bot.get_user(item.discord_id)  # TODO: since its an async now, you can probably use fetch
            user = await self.bot.fetch_user(item.discord_id)
            embed.set_thumbnail(url=user.display_avatar.url) if user else 0
            # all other fields
            embed.add_field(name='Registered Height', value=item.height, inline=True)
            embed.add_field(name='location', value=item.location.value, inline=True)
            embed.add_field(name='suspended', value=item.is_suspended, inline=True)
            embed.add_field(name='banned', value=item.is_banned)
            # Resolve the teams and games
            item.teams = await TeamBase.find(In(*ElemMatch('members',{}),[item.to_ref()]), with_children=True).to_list()
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
                embed = embed  # TODO: make private embed of Player
        return [embed]

    async def dashboard(self,
                        msg: Optional[discord.WebhookMessage] = None,
                        prev: Optional = None,
                        text: Optional[str] = None,
                        engine: Optional[E] = None) -> discord.ui.View:
        dashboard = await super().dashboard(msg=msg, prev=prev, text=text, engine=self)
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(FindButton(engine=self, search_function=self.get_by))
         .add_item(CreateButton())
         .add_item(UpdateButton())
         .add_item(DeleteButton()))
        return dashboard

    async def find_by_modal(self, inter, search_function: Callable, items: Optional = None) -> AsyncGenerator:
        """ used to return a Modal Instance """
        items = [NameInput(), LocationInput(), TeamInput(), CaptainInput(), BannedInput()]
        results = await super().find_by_modal(inter, search_function, items)
        return results

    def get_by(self, *,
                     name: Optional[str] = None,
                     discord_member: Optional[int] = None,
                     game: Optional[GameBase] = None,
                     location: Optional[str] = None,
                     banned: Optional[bool] = None,
                     suspended: Optional[bool] = None,
                     captain: Optional[Union[bool, str]] = None,
                     co_captain: Optional[Union[bool, str]] = None,
                     team: Optional[Union[TeamBase, str]] = None,
                     output: Optional[SearchOutputType] = SearchOutputType.NoLinksToList) -> AsyncGenerator:
        # dashboard searches is name, game, location, banned, captain,
        if captain:
            base = CaptainPlayer
        elif co_captain:
            base = CoCaptainPlayer
        else:
            base = PlayerEngine.base

        search = base.find({}, with_children=True)

        if name:
            search = search.find(RegEx(base.name, f'(?i){name}'))
        if discord_member:
            search = search.find(Eq(base.discord_id, discord_member))
        if game:
            # game = await GameBase.find(RegEx(GameBase.name, f'(?i){game}'), with_children=True).first_or_none()
            # TODO: need to find a way for ^^ this to search game names inside players via aggregate
            search = search.find(ElemMatch(base.games, {'$in': [game]}))
        if team:  # need to write if team is passed by str
            if isinstance(team, str):
                search = search.find(ElemMatch(base.teams, {'name': {'$regex': f'(?i){team}'}}))
                # search = search.find(ElemMatch(base.teams, RegEx(TeamBase.name, f'(?i){name}')))
            else:
                search = search.find(ElemMatch(base.teams, {'$in': [team]}))
        if location:
            # if you got a search phrase, parse it.
            search = search.find(RegEx(base.location, f'(?i){location}'))
            # search = search.find(Eq(base.location, location))
        if banned is not None:
            flag = True if banned.lower() in ["yes", "true", "y", "1", "affirmative", "ok", "okay",
                                              "positive"] else False
            search = search.find(Eq(base.is_banned, flag))
        if suspended is not None:
            search = search.find(Eq(base.is_suspended, True))

        return self.results_cursor(search)


    async def carousel(self, *,
                       msg=None,
                       prev: Optional[Awaitable] = None,
                       first: Optional[NamedTuple] = None,
                       generator: AsyncGenerator = None,
                       engine: Optional[E] = None) -> CarouselView:
        """ Used to return a Carousel"""
        carousel = await super().carousel(msg=msg, prev=prev, first=first, generator=generator, engine=self)
        carousel.embeds = await self.embed_maker(first.item)
        (carousel.add_item(UpdateButton())
         .add_item(DeleteButton()))
        return carousel


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
