from discord import Client, TextChannel, Message, Embed
from discord.ext import tasks, commands
from discord.ui import View

from routers.admin import get_settings, set_settings

from models.settings import SettingsModel

from views.players import PlayerRegisterPersistent
from views.teams import TeamRegisterPersistent

from embeds.players import PlayerRegisterEmbed
from embeds.teams import TeamRegisterEmbed


async def process_messages(s_channel: TextChannel, s_message: Message, embed: Embed, view: View) -> Message:
    async for last_message in s_channel.history(limit=1):
        if last_message != s_message:
            await s_message.delete()
            new_message = await s_channel.send(embed=embed, view=view)
            return new_message


class HelperTasks(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot
        self.reposter.start()

    def cog_unload(self) -> None:
        self.reposter.cancel()

    @tasks.loop(hours=24)
    async def reposter(self):
        settings = SettingsModel(**await get_settings())

        if settings.teams_channel:
            s_channel = self.bot.get_channel(settings.teams_channel)
            if s_message := await s_channel.fetch_message(settings.teams_message):
                if new_message := await process_messages(s_channel, s_message, TeamRegisterEmbed(),
                                                         TeamRegisterPersistent()):
                    settings.teams_message = new_message.id

        if settings.players_channel:
            channel = self.bot.get_channel(settings.players_channel)
            if s_message := await channel.fetch_message(settings.players_message):
                if new_msg := await process_messages(channel, s_message, PlayerRegisterEmbed(),
                                                     PlayerRegisterPersistent()):
                    settings.players_message = new_msg.id
        await set_settings(settings)

    @reposter.before_loop
    async def before_checks(self):
        print('Reposter is waiting for bot to start...')
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(HelperTasks(bot))
