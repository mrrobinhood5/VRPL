import discord
from discord import Interaction
from engines import BaseEngine, GameEngine
from typing import Any


class AdminEngine(BaseEngine):

    class AdminView(discord.ui.View):

        def __init__(self):
            super().__init__()
            self._msg = None
            self._embed = (discord.Embed(colour=discord.Colour.orange(),
                                         title='Admin Dash',
                                         description='Top Level Admin Options')
                           .set_thumbnail(url='https://i.imgur.com/VwQoXMB.png'))
            self.next = None

        def set_msg(self, msg: discord.WebhookMessage):
            self._msg = msg

        @property
        def msg(self):
            return self._msg

        @property
        def embed(self):
            return self._embed

        @discord.ui.button(custom_id='admin_view.games', style=discord.ButtonStyle.primary, label='Games')
        async def games(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Game Menu', embed=None, view=None)
            self.stop()
            self.next = inter.client.ge

        @discord.ui.button(custom_id='admin_view.players', style=discord.ButtonStyle.primary, label='Players')
        async def players(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Player Menu', embed=None, view=None)
            self.stop()
            self.next = inter.client.pe

        @discord.ui.button(custom_id='admin_view.teams', style=discord.ButtonStyle.primary, label='Teams')
        async def teams(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Teams Menu', embed=None, view=None)
            self.stop()
            self.next = inter.client.te

        async def on_timeout(self) -> None:
            await self.msg.delete()

        async def on_error(self, inter: Interaction, error: Exception, item: discord.ui.Item[Any], /) -> None:
            await self.msg.edit(content=f'{error.args} on {item}')

    def __init__(self):
        BaseEngine.ae = self
        self.dashboard: discord.ui.View = self.AdminView()

