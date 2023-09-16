import discord

from engines import *
from engines.base import BaseEngine
from models.games import GameBase
from pydantic import ValidationError, BaseModel
from typing import TypeVar, Type, Optional
from beanie.operators import RegEx
from discord import Interaction

B = TypeVar('B', bound=GameBase)


class GameNames(BaseModel):
    name: str


class GameEngine(BaseEngine):
    base = GameBase

    class GameView(BaseEngine.DashboardView):

        def __init__(self, msg: Optional[discord.WebhookMessage] = None,
                     caller: Optional = None):
            super().__init__(msg, caller)
            self._embed = (discord.Embed(colour=discord.Colour.dark_blue(),
                                         title='Game Dash',
                                         description='Game Options')
                           .set_thumbnail(url='https://i.imgur.com/VwQoXMB.png'))

        @discord.ui.button(custom_id='games_view.find', style=discord.ButtonStyle.secondary, label='Find By')
        async def find(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Find', embed=None, view=None)
            self.stop()
            self.next = None
            await self.msg.delete() # TODO: This is how dashboards will go ^^

        @discord.ui.button(custom_id='games_view.create', style=discord.ButtonStyle.secondary, label='Create')
        async def create(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Create', embed=None, view=None)
            self.stop()

        @discord.ui.button(custom_id='games_view.update', style=discord.ButtonStyle.secondary, label='Update')
        async def update(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Update', embed=None, view=None)
            self.stop()

        @discord.ui.button(custom_id='games_view.delete', style=discord.ButtonStyle.secondary, label='Delete')
        async def delete(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Delete', embed=None, view=None)
            self.stop()



    def __init__(self):
        # BaseEngine.engines.update({'GameEngine': self})
        pass



    async def get_by(self, name: Optional[str] = None,
                     output: Optional[SearchOutputType] = SearchOutputType.WithLinksToList) -> Optional[Union[list[B], B]]:
        base = GameEngine.base
        search = base.find({}, with_children=True,
                           fetch_links=True if output in [SearchOutputType.WithLinksToList,
                                                          SearchOutputType.WithLinksOnlyOne] else False)

        if name:
            search = search.find(RegEx(base.name, f'(?i){name}'))

        match output:
            case SearchOutputType.WithLinksToList | SearchOutputType.NoLinksToList:
                return await search.to_list()
            case SearchOutputType.WithLinksOnlyOne | SearchOutputType.NoLinksOnlyOne:
                return await search.first_or_none()
            case SearchOutputType.OnlyNames:
                return await search.project(GameNames).to_list()
            case _:
                return await search.to_list()

    # async def get_one_by_name(self, name: str) -> Optional[B]:
    #     return await base.find(RegEx(base.name, f'(?i){name}'), with_children=True, fetch_links=True).first_or_none()
    #
    # async def get_by_name(self, name: str) -> Optional[list[B]]:
    #     return await base.find(RegEx(base.name, f'(?i){name}'), with_children=True, fetch_links=True).to_list()
    #
    # async def all_games_names(self) -> list:
    #     return await base.find({}, with_children=True).project(GameShortView).to_list()

    async def create_game(self, base: Type[B] = Game, **kwargs) -> Type[B]:
        try:
            game = await base(**kwargs).insert()
            return game
        except ValidationError as e:
            raise e

