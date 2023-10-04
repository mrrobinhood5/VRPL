from functools import wraps

from models import VRPLObject
from typing import Type, TypeVar
from pydantic import ValidationError
from .shared import *

B = TypeVar('B', bound=VRPLObject)
E = TypeVar('E', bound='BaseEngine')


# MAIN BASE ENGINE
class BaseEngine:
    base = VRPLObject
    engines = {}

    def __init__(self, bot=None):
        self.bot = bot

    # HELPER methods
    @staticmethod
    async def results_cursor(cursor) -> Result:
        try:
            count = await cursor.count()
        except AttributeError as e:
            count = len(await cursor.to_list())
        async for result in cursor:
            r = Result(item=result, count=count)

            yield r

    # VIEW methods

    @staticmethod
    def embed_maker(embed_func):
        """ A decorator function that generates embeds for the dashboard or carousels in the specified

        Parameters
        -----------
        item: :class:`VRPLObject`
            Any VRPL Object that is to have an embed representation
        private: bool
            Boolean to add a private information Embed
        """
        @wraps(embed_func)
        async def wrapped_embed_maker(self, /, *args, **kwargs) -> list[discord.Embed]:

            public = discord.Embed(title='Public View', description="Default Public Description")
            public.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
            private = discord.Embed(title='Private View', description="Default Private Description")
            private.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')

            embeds = Embeds(private, public)
            embeds = await embed_func(self, item=kwargs.get('item'), private=kwargs.get('private'), embeds=embeds)
            return embeds
        return wrapped_embed_maker

    @staticmethod
    def dashboard(dashboard_func):
        """ A decorator that generates a dashboard view.

        The function deocrated needs to have, ``self`` representing the :class:`BaseEngine`,
        and the :class:`DashboardView` being processed.

        .. note ::
            You must add the required Buttons for that specific Dashboard in the decorated function

        Parameters
        ____________

        msg: :class:`discord.WebhookMessage`
            The message that is being used for the Dashboard
        prev: :class:`Callable`
            The view that will be used when the Back Button is pressed (usually the previous view passes itself)
        text: Optional[`str`]
            In case the view will not do anything, a message that represents what went wrong
        engine: :class:`BaseEngine`
            The Engine that will be used inside the view to process other methods

        :return: `DashboardView`"""
        @wraps(dashboard_func)
        async def wrapped_dashboard(self, /, *args, **kwargs) -> discord.ui.View:
            dashboard = DashboardView(*args, **kwargs)
            dashboard.add_item(DoneButton()).add_item(BackButton(next=kwargs.get('prev')))
            dashboard = await dashboard_func(self, *args, **kwargs, dashboard=dashboard)
            return dashboard

        return wrapped_dashboard

    @staticmethod
    def find_by_modal(find_by_func):
        """ A decorater that generates a Modal to Search By """
        @wraps(find_by_func)
        async def wrapped_modal(self, /,
                                inter: discord.Interaction,
                                search_function: Callable,
                                *args, **kwargs) -> Result:
            print(f'Inside BaseEngine.find_by_modal self is {self}')
            view = Modal() # TODO: this modal sometimes will add pre filled fields such as when retrieving discord member data
            if (i:=kwargs.get('inputs')):
                [view.add_item(x) for x in i]
            view = await find_by_func(self, modal=view)
            await inter.response.send_modal(view)
            await view.wait()
            print(f'sending results to {search_function}')
            results = search_function(**view.results)
            print(f'results from BaseEngine.find_by_modal are: {results}')
            return results
        return wrapped_modal


    @staticmethod
    def create_modal(create_modal_func):
        @wraps(create_modal_func)
        async def wrapped_create_func(self, /,
                                      inter: discord.Interaction,
                                      search_function: Callable,
                                      engine: BaseEngine,
                                      *args, **kwargs) -> Result:
            """ used to start a Creation Modal, add your items by subclassing in the specific engine """
            view = Modal()
            if (i:= kwargs.get('inputs')):
                [view.add_item(x) for x in i]
            view = await create_modal_func(self, modal=view, inter=inter)
            await inter.response.send_modal(view)
            await view.wait()
            created = await engine.create_function(document=view.results)
            results = search_function(id=created.id)
            return results
        return wrapped_create_func

    @staticmethod
    def carousel(carousel_func):
        async def wrapped_carousel(self, /, *args, **kwargs) -> CarouselView:
            """ A decorator that generates a dashboard view.

            The function deocrated needs to have, ``self`` representing the :class:`BaseEngine`,
            and the :class:`DashboardView` being processed.

            .. note ::
                You must add the required Buttons for that specific Dashboard in the decorated function

            Parameters
            ____________

            msg: :class:`discord.WebhookMessage`
                The message that is being used for the Dashboard
            count: int
                The total number of items cin the generator
            embeds: list[`discord.ui.Embed`]
                The embeds needed for the first item
            first_item: :class:`VRPLObject`
                Any VRPL object returned from a Result lookup
            prev: Awaitable
                a callback function to run when the back button is pressed. e.g. a `carousel` or `dashboard` function
            generator: :class:`Result`
                the generator to draw the next items for the carousel
            engine:
                the current engine
            :return: `CarouselView`"""
            carousel = CarouselView(*args, **kwargs)
            carousel.add_item(DoneButton()).add_item(BackButton(next=kwargs.get('prev')))
            return carousel
        return wrapped_carousel


    async def get_by(self, *args, **kwargs):
        raise NotImplementedError('Not implemented in this SubClass')

    async def create_function(self, base, document, *args, **kwargs):
        try:
            team = await base(**document).insert()
            return team
        except ValidationError as e:
            raise e

    # Agnostic Functions
    async def count(self, base: Optional[Type[B]] = base) -> int:
        return await base.find({}, with_children=True).count()

    # NOT IMPLEMENTED YET
    async def update(self, base: Type[B], updates: dict) -> Type[B]:
        try:
            return await base.set(updates)
        except ValidationError as e:
            raise e
