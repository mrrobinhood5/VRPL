import discord
from beanie import init_beanie
from database import Database
from config import BOT_TOKEN
from custom import bot
from utils import all_models

discord.utils.setup_logging()

extensions = ['cogs.admin']


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID: {bot.user.id})')
    activity = discord.Game('Contractor$ on Quest 3')
    await bot.change_presence(status=discord.Status.online, activity=activity)
    await bot.load_extensions(extensions)
    await bot.load_engines()

    # Need a better way to register all persistent views maybe from the DB
    # bot.add_view(PlayerRegisterPersistent())
    # bot.add_view(TeamRegisterPersistent())

    await init_beanie(database=Database().db, document_models=all_models(), recreate_views=True)



bot.run(BOT_TOKEN)
