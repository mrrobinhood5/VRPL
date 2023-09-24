
from engines.shared import *
from engines.base import BaseEngine
from typing import Any, Optional, TypeVar

E = TypeVar('E', bound=BaseEngine)


class AdminEngine(BaseEngine):

    @classmethod
    async def embed_maker(cls, item: Optional[Any] = None, private: Optional[bool] = False) -> list[discord.Embed]:
        if not item:
            embed = discord.Embed(title="Admin Dashboard", description="Administrator Options")
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
            return [embed]

    async def dashboard(self,
                  msg: Optional[discord.WebhookMessage] = None,
                  prev: Optional = None,
                  text: Optional[str] = None,
                  engine: Optional[E] = None) -> discord.ui.View:
        dashboard = await super().dashboard(msg, prev, text, self)
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(DashButton(label='Games', next=self.bot.ge))
                  .add_item(DashButton(label='Players', next=self.bot.pe))
                  .add_item(DashButton(label='Teams', next=self.bot.te)))
        return dashboard

