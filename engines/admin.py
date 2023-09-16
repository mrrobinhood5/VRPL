import discord
from discord import Interaction
from engines import BaseEngine, GameEngine
from typing import Any, Optional


class AdminEngine(BaseEngine):

    class DashboardView(BaseEngine.DashboardView):

        def __init__(self, msg: Optional[discord.WebhookMessage] = None,
                     caller: Optional = None):
            super().__init__(msg, caller)
            self._embed = (discord.Embed(colour=discord.Colour.orange(),
                                         title='Admin Dash',
                                         description='Top Level Admin Options')
                           .set_thumbnail(url='https://i.imgur.com/VwQoXMB.png'))


        @discord.ui.button(custom_id='admin_view.games', style=discord.ButtonStyle.primary, label='Games')
        async def games(self, inter: Interaction, button: discord.ui.Button):
            # await self.msg.delete()
            await self.msg.edit(content='Accessing Game Menu', embed=None, view=None)
            self.stop()
            self.next = inter.client.ge
            await self.msg.delete()  # TODO: This is how dashboards will go ^^

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

    def __init__(self):
        pass
        # Register itself with BaseEngine, why? I really don't know
        # BaseEngine.engines.update({'AdminEngine': self})

