from discord import Client, TextChannel, Message, Embed
from discord.ext import tasks, commands
from discord.ui import View
from custom import VRPLBot

from models.players import PlayerRegisterPersistent
from models.teams import TeamRegisterPersistent


async def process_messages(channel: TextChannel, message: Message, embed: Embed, view: View) -> Message:
    async for last_message in channel.history(limit=1):
        if last_message != message:
            await message.delete()
            new_message = await channel.send(embed=embed, view=view)
            return new_message


class HelperTasks(commands.Cog):
    def __init__(self, bot):
        self.bot: VRPLBot = bot
        self.reposter.start()

    def cog_unload(self) -> None:
        self.reposter.cancel()

    @tasks.loop(hours=24)
    async def reposter(self):
        if channel := self.bot.settings.teams_channel:
            if message := await channel.fetch_message(self.bot.settings.teams_message_id):
                persistent = TeamRegisterPersistent()
                if new_message := await process_messages(channel, message, persistent.embed(), persistent):
                    self.bot.settings.teams_message_id = new_message.id

        if channel := self.bot.settings.players_channel:
            if message := await channel.fetch_message(self.bot.settings.players_message_id):
                persistent = PlayerRegisterPersistent()
                if new_message := await process_messages(channel, message, persistent.embed(), persistent):
                    self.bot.settings.players_message = new_message.id
        self.bot.settings.save()

    @reposter.before_loop
    async def before_checks(self):
        print('Reposter is waiting for bot to start...')
        await self.bot.wait_until_ready()



async def setup(bot: commands.Bot):
    await bot.add_cog(HelperTasks(bot))
