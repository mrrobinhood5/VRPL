import discord
from discord import Interaction
from typing import Optional, Any, Callable, Literal, Awaitable, AsyncGenerator, NamedTuple

    # MODALS
class FindByModal(discord.ui.Modal, title=""):
    """ Overwrite me for each type of model"""
    async def on_submit(self, inter: Interaction) -> None:
        await inter.response.defer()
        self.results = {item.label: item.value for item in self.children}
        print(self.results)
        self.stop()

# INPUTS
class NameInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='name', placeholder='Leave Blank for ALL', required=False)

class PlayerInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='member', placeholder='Leave Blank for ALL', required=False)

class RegionInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='region', placeholder='Leave Blank for ALL', required=False)

class GameInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='game', placeholder='Leave Blank for ALL', required=False)

class LocationInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='location', placeholder='Leave Blank for ALL', required=False)

class TeamInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='team', placeholder='Leave Blank for ALL', required=False)

class CaptainInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='captain', placeholder='Yes, No, or Blank for BOTH', required=False)

class BannedInput(discord.ui.TextInput):
    def __init__(self):
        super().__init__(label='banned', placeholder='Yes, No, or Blank for BOTH', required=False)


#BUTTONS
class DashButton(discord.ui.Button):
    def __init__(self, label: str, next: Awaitable):
        super().__init__(label=label, style=discord.ButtonStyle.green)
        self.next = next

    async def callback(self, inter: Interaction) -> Any:
        await inter.response.defer()
        self.view.next = self.next.dashboard(prev=self.view.engine.dashboard, msg=self.view.msg)
        self.view.stop()

class InfoButton(discord.ui.Button):

    def __init__(self, label):
        super().__init__(custom_id='counter', label=label, style=discord.ButtonStyle.grey)

    async def callback(self, inter: Interaction):
        # TODO: This will call the next View which is the individual view
        await inter.response.defer()
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        # await inter.response.edit_message(view=self.view)

class ControlButton(discord.ui.Button):

    def __init__(self, action: Literal['next', 'previous']):
        self.action = action
        label = "Next >" if action == 'next' else "< Previous"
        super().__init__(label=label, style=discord.ButtonStyle.green)

    async def callback(self, inter: Interaction):
        await inter.response.defer()
        if self.action == 'next':
            if self.view.item_index == len(self.view.items) - 1: # its the last item
                try:
                    item = await anext(self.view.generator)
                    self.view.items.append(item.item)
                    self.view.item_index += 1
                except StopAsyncIteration as e:
                    self.view.item_index = (self.view.item_index + 1) % self.view.item_count

            else: # its not the last item
                self.view.item_index += 1

        if self.action == 'previous':
            self.view.item_index = (self.view.item_index - 1) % self.view.item_count
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        # await self.view.update_view(inter, self.view.item)
        await self.view.msg.edit(embeds=await self.view.engine.embed_maker(self.view.item), view=self.view)



class FindButton(discord.ui.Button):
    def __init__(self, *, engine , search_function: Callable):
        super().__init__(custom_id='find_button', label='FindBy', style=discord.ButtonStyle.green)
        self.engine = engine # this is an engine
        self.search_function = search_function # this is a function to be used by find callback

    async def callback(self, inter: Interaction):
        await self.view.msg.edit(content='Accessing FindBy', embed=None, view=None)
        results = await self.engine.find_by_modal(inter, self.search_function)

        # TODO: Making results an AsyncGenerator loses the capability to know if its empty or not, so the back function is not gonna work like this
        try:
            first = await anext(results)
        except StopAsyncIteration as e:
            first = None
        if not first:
            self.view.next = self.engine.dashboard(msg=self.view.msg, prev=self.view.prev, text='No results Found')
        else:
            self.view.next = self.engine.carousel(msg=self.view.msg, first=first, generator=results, prev=self.view.engine.dashboard)
        # this is what needs to be as previous
        #
        self.view.stop()

class CreateButton(discord.ui.Button):
    def __init__(self):
        super().__init__(custom_id='create_button', label='Create', style=discord.ButtonStyle.green)

    async def callback(self, inter: Interaction):
        await self.view.msg.edit(content='Accessing Create', embed=None, view=None)
        self.view.stop()
        self.view.next = inter.engine.create() # TODO: this is wrong
        self.view.prev = inter.engine.dashboard(prev=self.view.prev)

class UpdateButton(discord.ui.Button):
    def __init__(self):
        super().__init__(custom_id='update_button', label='Update', style=discord.ButtonStyle.green)

    async def callback(self, inter: Interaction):
        await self.view.msg.edit(content='Accessing Update', embed=None, view=None)
        self.view.stop()
        self.view.next = inter.engine.update()
        self.view.prev = inter.engine.dashboard(prev=self.view.prev)

class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(custom_id='delete_button', label='Delete', style=discord.ButtonStyle.green)

    async def callback(self, inter: Interaction):
        await self.view.msg.edit(content='Accessing Delete', embed=None, view=None)
        self.view.stop()
        self.view.next = inter.engine.delete()
        self.view.prev = inter.engine.dashboard(prev=self.view.prev)

class DoneButton(discord.ui.Button):
    def __init__(self):
        super().__init__(custom_id='done_button', style=discord.ButtonStyle.gray, label='Done', row=2)

    async def callback(self, inter: Interaction):
        await inter.response.defer()
        self.view.stop()
        self.view.next = None
        await self.view.msg.delete()

class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(custom_id='back_button', style=discord.ButtonStyle.gray, label='Back', row=2)

    async def callback(self, inter: Interaction):
        await inter.response.defer()
        self.view.stop()
        self.view.next = self.view.prev
        await self.view.msg.delete()

# VIEWS
class DashboardView(discord.ui.View):

    def __init__(self, *,
                 msg: Optional[discord.WebhookMessage] = None,
                 prev: Optional[Callable] = None,
                 text: Optional[str] = None,
                 engine: Optional = None):
        """ msg: So the buttons can edit when clicked, and delete itself before restarting the cycle
            prev: This gets passed on with every next() attribute """
        super().__init__()
        self._msg: Optional[discord.WebhookMessage] = msg
        self._embeds: Optional[list[discord.Embed]] = [discord.Embed()]
        self._engine = engine
        self.next: Optional[Awaitable] = None
        self.prev: Optional[Awaitable] = prev
        self.text = text or ''

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, engine):
        self._engine = engine

    @property
    def msg(self) -> discord.WebhookMessage:
        return self._msg

    @msg.setter
    def msg(self, msg) -> None:
        self._msg = msg

    @property
    def embeds(self) -> list[discord.Embed]:
        return self._embeds

    @embeds.setter
    def embeds(self, embeds: list[discord.Embed]) -> None:
        self._embeds = embeds

class CarouselView(DashboardView):
    def __init__(self, *,
                 msg: discord.WebhookMessage,
                 prev: Optional[Awaitable] = None,
                 first: Optional[NamedTuple] = None,
                 generator: AsyncGenerator,
                 engine: Optional[None]):
        super().__init__(msg=msg, prev=prev, engine=engine)
        self.items: list[Any] = [first]
        self.generator = generator
        self.item_index = 0
        self.item_count = first.count
        self.timeout = None
        self.previous = ControlButton(action='previous')
        self.counter = InfoButton(label=f'1 of {first.count}')
        self.next = ControlButton(action='next')

        self.add_item(self.previous).add_item(self.counter).add_item(self.next)

    @property
    def item(self):
        return self.items[self.item_index]

