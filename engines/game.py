import discord

from engines.shared import *
from engines.base import BaseEngine
from models import SearchOutputType
from models.games import GameBase, AllTeamNamesByGame, Game
from pydantic import ValidationError, BaseModel
from typing import TypeVar, Type, Optional, Literal, Callable, Any, Union, AsyncGenerator, NamedTuple
from beanie.operators import RegEx
from discord import Interaction

B = TypeVar('B', bound=GameBase)
E = TypeVar('E', bound=BaseEngine)


class GameNames(BaseModel):
    name: str


class GameEngine(BaseEngine):
    base = GameBase

    async def embed_maker(self, item: Optional[NamedTuple] = None, private: Optional[bool] = False) -> list[discord.Embed]:

        if not item:
            embed = discord.Embed(title="Games Dashboard", description="Options for managing League Games")
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
        else:
            item = item.item
            embed = discord.Embed(title=item.name, description=item.description)
            # embed.set_thumbnail(url=item.thumbnail) if item.thumbnail else 0
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
            teams = ''.join([f"`{team}` " for team in item.teams])
            embed.add_field(name='Teams', value=teams)
            if private:
                embed = embed  # TODO: make private embed of Games
        return [embed]

    async def dashboard(self,
                        msg: Optional[discord.WebhookMessage] = None,
                        prev: Optional = None,
                        text: Optional[str] = None,
                        engine: Optional[E] = None) -> discord.ui.View:
        dashboard = await super().dashboard(msg=msg, prev=prev, text=text, engine=self)
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(FindButton(engine=self, search_function=self.get_teams_by_game))
         .add_item(CreateButton())
         .add_item(UpdateButton())
         .add_item(DeleteButton()))
        return dashboard

    async def find_by_modal(self, inter, search_function: Callable, items: Optional = None) -> AsyncGenerator:
        """ used to return a Modal Instance , add your items relevant """
        items = [NameInput()]
        results = await super().find_by_modal(inter, search_function, items)
        return results

    # SEARCH methods
    def get_teams_by_game(self, name: Optional[str] = None) -> type[AsyncGenerator, int]:
        x = AllTeamNamesByGame.find(RegEx('_id', f'(?i){name if name else ""}'))
        return self.results_cursor(x)

    async def carousel(self, *,
                       msg=None,
                       prev: Optional[Awaitable] = None,
                       first: Optional[NamedTuple] = None,
                       generator: AsyncGenerator = None,
                       engine: Optional[E] = None) -> CarouselView:
        carousel = await super().carousel(msg=msg, prev=prev, first=first, generator=generator, engine=self)
        carousel.embeds = await self.embed_maker(first)
        (carousel.add_item(UpdateButton())
         .add_item(DeleteButton()))
        return carousel

    # NOTHING BELOW IS IMPLEMENTED
    async def get_by(self, name: Optional[str] = None,
                     output: Optional[SearchOutputType] = SearchOutputType.NoLinksToList) -> Optional[Union[list[B], B]]:
        """ Used to do a query """ # TODO: I dont think this is uused
        base = GameEngine.base
        search = base.find({}, with_children=True)

        if name:
            search = search.find(RegEx(base.name, f'(?i){name}'))

        match output:
            case SearchOutputType.WithLinksToList:
                return await search.find(fetch_links=True).to_list()
            case SearchOutputType.NoLinksToList:
                return await search.to_list()
            case SearchOutputType.WithLinksOnlyOne:
                return await search.find(fetch_links=True).first_or_none()
            case SearchOutputType.NoLinksOnlyOne:
                return await search.first_or_none()
            case SearchOutputType.OnlyNames:
                return await search.project(GameNames).to_list()
            case _:
                return await search.to_list()

    async def create_game(self, base: Type[B] = Game, **kwargs) -> Type[B]:
        try:
            game = await base(**kwargs).insert()
            return game
        except ValidationError as e:
            raise e
