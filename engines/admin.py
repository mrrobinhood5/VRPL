from engines.shared import *
from engines.base import BaseEngine
from typing import Any, Optional, TypeVar

E = TypeVar('E', bound=BaseEngine)


class AdminEngine(BaseEngine):

    @BaseEngine.embed_maker
    async def embed_maker(self,
                          embeds=Embeds, item: Optional[Any] = None,
                          private: Optional[bool] = False) -> list[discord.Embed]:
        if not item: # this means its a dashboard
            embed = embeds.public
            embed.title = 'Admin Dashboard'
            embed.description = 'Options to Manage other Dashboards as Admin'
            return [embed]

    @BaseEngine.dashboard
    async def dashboard(self, /, dashboard: discord.ui.View, *args, **kwargs) -> discord.ui.View:
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(DashButton(label='Games', next=self.bot.ge, prev=self.dashboard))
         .add_item(DashButton(label='Players', next=self.bot.pe, prev=self.dashboard))
         .add_item(DashButton(label='Teams', next=self.bot.te, prev=self.dashboard)))
        return dashboard
