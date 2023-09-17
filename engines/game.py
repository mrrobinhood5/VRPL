import discord

from engines import *
from engines.base import BaseEngine
from models.games import GameBase
from pydantic import ValidationError, BaseModel
from typing import TypeVar, Type, Optional, Literal
from beanie.operators import RegEx
from discord import Interaction

B = TypeVar('B', bound=GameBase)


class ControlButton(discord.ui.Button):

    def __init__(self, action: Literal['next', 'previous']):
        self.action = action
        label = "Next >" if action == 'next' else "< Previous"
        super().__init__(label=label, style=discord.ButtonStyle.green)

    async def callback(self, inter: Interaction):
        item = next(self.view.next_item if self.action == 'next' else self.view.prev_item)
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        await self.view.update_view(inter, item)


class InfoButton(discord.ui.Button):

    def __init__(self):
        super().__init__(custom_id='counter', label='1 of x', style=discord.ButtonStyle.grey)

    async def callback(self, inter: Interaction):
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        await inter.response.edit_message(view=self.view)


class GameNames(BaseModel):
    name: str


class GameEngine(BaseEngine):
    base = GameBase

    class GameCarousel(discord.ui.View): # TODO: I left off in the carousel to dis
        def __init__(self, msg, prev, results):
            super().__init__()
            self.msg = msg
            self.prev = prev
            self.next = None

            #carousel vars
            self.results: list[Type[B]] = results
            self.item_index = 0
            self.timeout = None

            self.previous = ControlButton(action='previous')
            self.counter = InfoButton()
            self.next = ControlButton(action='next')

            self.add_item(self.previous).add_item(self.counter).add_item(self.next)

        async def update_view(self, inter: Interaction, item):
            await inter.response.edit_message(embed=item.embed, view=self)

        @discord.ui.button(style=discord.ButtonStyle.gray, label='Done', row=2)
        async def done(self, inter: Interaction, button: discord.ui.Button):
            await inter.response.defer()
            self.stop()
            self.next = None
            await self.msg.delete()

        @discord.ui.button(style=discord.ButtonStyle.gray, label='Back', row=2)
        async def back(self, inter: Interaction, button: discord.ui.Button):
            await inter.response.defer()
            self.stop()
            self.next = self.prev
            await self.msg.delete()

    class FindByModal(discord.ui.Modal, title="Game: Find By"): # Remeber, a Modal is essentially a view

        name = discord.ui.TextInput(label="Name") # TODO: A lot of these TextInputs are repeated, maybe define them somewhere else

        def __init__(self):
            super().__init__()
            self.result = None

        async def on_submit(self, inter: Interaction) -> None:
            await inter.response.defer()
            self.result = await inter.client.ge.get_by(name=self.name.value, output=SearchOutputType.WithLinksToList)
            print(self.result)
            # this is where the query gets put together and gets sent back as a list for the Carousel

    class DashboardView(BaseEngine.DashboardView):

        def __init__(self, msg: Optional[discord.WebhookMessage] = None, prev: Optional = None):
            super().__init__(msg, prev)
            self._embed = (discord.Embed(colour=discord.Colour.dark_blue(),
                                         title='Game Dash',
                                         description='Game Options')
                           .set_thumbnail(url='https://i.imgur.com/VwQoXMB.png'))

        @discord.ui.button(custom_id='games_view.find', style=discord.ButtonStyle.green, label='Find By')
        async def find(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Find', embed=None, view=None)
            self.stop()
            results = await inter.client.ge.find_by_modal(inter)
            self.next = inter.client.ge.display_results(results)
            self.prev = inter.client.ge.dashboard(prev=self.prev)
            await self.msg.delete()


        @discord.ui.button(custom_id='games_view.create', style=discord.ButtonStyle.green, label='Create')
        async def create(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Create', embed=None, view=None)
            self.stop()
            self.next = inter.client.ge.create()
            self.prev = inter.client.ge.dashboard(prev=self.prev)

        @discord.ui.button(custom_id='games_view.update', style=discord.ButtonStyle.green, label='Update')
        async def update(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Update', embed=None, view=None)
            self.stop()
            self.next = inter.client.ge.update()
            self.prev = inter.client.ge.dashboard(prev=self.prev)

        @discord.ui.button(custom_id='games_view.delete', style=discord.ButtonStyle.green, label='Delete')
        async def delete(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Delete', embed=None, view=None)
            self.stop()
            self.next = inter.client.ge.delete()
            self.prev = inter.client.ge.dashboard(prev=self.prev)

    async def find_by_modal(self, inter):
        """ used to return a Modal Instance """
        view = self.FindByModal()
        await inter.response.send_modal(view)
        return view.result

    def display_results(self, results):
        """ used to return a Results View"""
        return self.GameCarousel(results=results)

    async def get_by(self, name: Optional[str] = None,
                     output: Optional[SearchOutputType] = SearchOutputType.WithLinksToList) -> Optional[Union[list[B], B]]:
        """ Used to do a query """
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

    async def create_game(self, base: Type[B] = Game, **kwargs) -> Type[B]:
        try:
            game = await base(**kwargs).insert()
            return game
        except ValidationError as e:
            raise e

