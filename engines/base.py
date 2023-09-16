from models import VRPLObject
from models.enums import SearchType
from typing import Type, TypeVar, Optional, List, Tuple, Dict
from pydantic import ValidationError, Field
import discord
from discord import Interaction


B = TypeVar('B', bound=VRPLObject)


class BaseEngine:

    base = VRPLObject
    engines = {}

    class DashboardView(discord.ui.View):

        def __init__(self, msg: Optional[discord.WebhookMessage] = None,
                     caller: Optional = None, engine = None):
            super().__init__()
            self.engine = engine
            self._called_by = caller
            self._msg = msg
            self._embed: Optional[discord.Embed] = discord.Embed()
            self.next: discord.ui.View = None

        @property
        def msg(self):
            return self._msg

        @msg.setter
        def msg(self, msg):
            self._msg = msg

        @property
        def embed(self):
            return self._embed

        @embed.setter
        def embed(self, embed):
            self._embed = embed

        @discord.ui.button(style=discord.ButtonStyle.gray, label='Done')
        async def done(self, inter: Interaction, button: discord.ui.Button):
            self.stop()
            self.next = None
            await self.msg.delete()

        @discord.ui.button(style=discord.ButtonStyle.gray, label='Back')
        async def back(self, inter: Interaction, button: discord.ui.Button):
            self.stop()
            self.next = self._called_by or None
            await self.msg.delete()

    def dashboard(self, msg: Optional[discord.WebhookMessage] = None,
                  caller: Optional = None, engine=engines): # TODO: I left of here, how to pass the caller engine to enable the back button
        return self.DashboardView(msg, caller, engine)

    async def count(self, base: Optional[Type[B]] = base) -> int:
        return await base.find({}, with_children=True).count()

    async def get_all(self, base: Type[B], f: Optional[dict] = None) -> list[B]:
        return await base.find(f if f else {}, with_children=True, fetch_links=True).to_list()

    async def get_all_basic(self, base: Optional[Type[B]] = base, f: Optional[dict] = None) -> list[Type[B]]:
        """ Same as get_all() but without fetching links """
        return await base.find(f if f else {}, with_children=True).to_list()

    async def get_by(self, *args, **kwargs):
        raise NotImplementedError('Not implemented in this SubClass')

    async def update(self, base: Type[B], updates: dict) -> Type[B]:
        try:
            return await base.set(updates)
        except ValidationError as e:
            raise e
