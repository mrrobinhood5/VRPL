import discord

from config import BOT_TOKEN
from custom import bot
from models.players import PlayerRegisterPersistent
from models.teams import TeamRegisterPersistent
from models.admin import SettingsModel

discord.utils.setup_logging()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID: {bot.user.id})')
    activity = discord.Game('Contractor$ on Quest 3')
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot.settings = SettingsModel.get()
    bot.add_view(PlayerRegisterPersistent())
    bot.add_view(TeamRegisterPersistent())

bot.run(BOT_TOKEN)
