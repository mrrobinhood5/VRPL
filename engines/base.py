from models import VRPLObject
from typing import Any, Type, TypeVar, AsyncGenerator, NamedTuple, Union
from collections import namedtuple
from pydantic import ValidationError, Field
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
    async def results_cursor(cursor) -> NamedTuple:
        Result = namedtuple('Result', ['item', 'count'])
        try:
            count = await cursor.count()
        except AttributeError as e:
            count = len(await cursor.to_list())
        async for result in cursor:
            r = Result(item=result, count=count)
            print(r)
            yield r

    # VIEW methods
    async def embed_maker(self, item: Optional[Any] = None, private: Optional[bool] = False) -> list[discord.Embed]:
        """ Implement embed maker to whatever engine you are in """
        pass

    async def dashboard(self,
                        msg: Optional[discord.WebhookMessage] = None,
                        prev: Optional = None,
                        text: Optional[str] = None,
                        engine: Optional[E] = None) -> discord.ui.View:
        """ Returns a default DashboardView, with default Embed, and both Done and Back buttons
         When subclassing call super and then add_item() for the extra buttons for each engine. """
        dashboard = DashboardView(msg=msg, prev=prev, text=text, engine=engine)
        dashboard.add_item(DoneButton()).add_item(BackButton(next=prev))
        return dashboard

    async def find_by_modal(self, inter, search_function: Callable, items: Optional = None) -> AsyncGenerator:
        """ used to return a Modal Instance , add your items relevant to each engine here"""
        view = FindByModal()
        [view.add_item(item) for item in items]
        await inter.response.send_modal(view)
        await view.wait()
        results = search_function(**view.results)
        return results

    async def carousel(self, *,
                       msg=None,
                       count: int,
                       embeds: list,
                       first_item: Type[B] = None,
                       prev: Optional[Awaitable] = None,
                       generator: AsyncGenerator = None,
                       engine: Optional[E] = None) -> CarouselView:
        """ Returs a Carousel View """
        carousel = CarouselView(msg=msg,
                                prev=prev,
                                count=count,
                                embeds=embeds,
                                first_item=first_item,
                                generator=generator,
                                engine=engine)
        carousel.add_item(DoneButton()).add_item(BackButton(next=prev))
        return carousel

    async def get_by(self, *args, **kwargs):
        raise NotImplementedError('Not implemented in this SubClass')

    async def count(self, base: Optional[Type[B]] = base) -> int:
        return await base.find({}, with_children=True).count()

    async def update(self, base: Type[B], updates: dict) -> Type[B]:
        try:
            return await base.set(updates)
        except ValidationError as e:
            raise e
