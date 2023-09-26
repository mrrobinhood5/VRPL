import discord

from engines.shared import *
from engines.base import BaseEngine
from models import SearchOutputType
from models.games import GameBase, AllTeamNamesByGame, Game
from pydantic import ValidationError, BaseModel
from typing import TypeVar, Type, Optional, Literal, Callable, Any, Union, AsyncGenerator, NamedTuple
from beanie.operators import RegEx
from monggregate import Pipeline

B = TypeVar('B', bound=GameBase)
E = TypeVar('E', bound=BaseEngine)


class GameNames(BaseModel):
    name: str


class GameEngine(BaseEngine):
    base = GameBase

    async def embed_maker(self, item: Type[B] = None, private: Optional[bool] = False) -> list[discord.Embed]:

        if not item:
            embed = discord.Embed(title="Games Dashboard", description="Options for managing League Games")
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png') # TODO: I left of here, gonna make games more like all other engines to use get_by and fix this embed
        else:
            embed = discord.Embed(title=item.name, description=item.description)
            # embed.set_thumbnail(url=item.thumbnail) if item.thumbnail else 0
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
            teams = ''.join([f"`{team.name}` " for team in item.teams])
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
        (dashboard.add_item(FindButton(engine=self, search_function=self.get_by))
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
                       count: int,
                       embeds: list,
                       first_item: Type[B] = None,
                       prev: Optional[Awaitable] = None,
                       generator: AsyncGenerator = None,
                       engine: Optional[E] = None) -> CarouselView:
        carousel = await super().carousel(msg=msg,
                                          count=count,
                                          embeds=embeds,
                                          first_item=first_item,
                                          prev=prev,
                                          generator=generator,
                                          engine=self)
        # carousel.embeds = await self.embed_maker(first)
        (carousel.add_item(UpdateButton())
         .add_item(DeleteButton()))
        return carousel

    # NOTHING BELOW IS IMPLEMENTED
    async def get_by(self, name: Optional[str] = None) -> AsyncGenerator:
        """ Used to do a query """ # TODO: rewirte to use this instead of teams by game
        base = GameEngine.base
        search = base.find({}, with_children=True)

        if name:
            search = search.find(RegEx(base.name, name, 'i'))
        pipeline = (Pipeline()
                    .lookup(right="TeamBase", left_on='_id', right_on='game.$id', name='teams')
                    .export())
        return self.results_cursor(search.aggregate(pipeline, projection_model=base))



    async def create_game(self, base: Type[B] = Game, **kwargs) -> Type[B]:
        try:
            game = await base(**kwargs).insert()
            return game
        except ValidationError as e:
            raise e
