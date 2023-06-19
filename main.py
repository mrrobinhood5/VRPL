import asyncio
import discord
import uvicorn

from fastapi import FastAPI

from discord.ext import commands

from config import BOT_TOKEN, INTENTS, BOT_PREFIX, BOT_OWNER, cogs

from routers import players, teams, team_join_approvals, admin

from views.players import PlayerRegisterPersistent
from views.teams import TeamRegisterPersistent


app = FastAPI()
bot = commands.Bot(command_prefix=BOT_PREFIX, description='VRPL Team Manager', intents=INTENTS)
bot.owner_id = int(BOT_OWNER)

discord.utils.setup_logging()

app.include_router(players.router)
app.include_router(teams.router)
app.include_router(team_join_approvals.router)
app.include_router(admin.router)


@app.get('/')
def read_root():
    """
    This Build Testing V2 creates
    - **5** Teams  *(Randomly Generated)*
    - **30** Players *(Randomly Generated)*

    Every restart, all the stats get rebuild from scratch.

    **THIS IS FOR TESTING AND PROOF OF CONCEPT ONLY**
    """
    return {"Testing": "ok"}


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID: {bot.user.id})')
    activity = discord.Game('Contractor$ on Quest 3')
    await bot.change_presence(status=discord.Status.online, activity=activity)
    for cog in cogs:
        print(f'cogs.{cog[:-3]}')
        await bot.load_extension(f'cogs.{cog[:-3]}')


@bot.event
async def setup_hook():
    bot.add_view(PlayerRegisterPersistent())
    bot.add_view(TeamRegisterPersistent())


@app.on_event('startup')
async def run_bot():
    asyncio.create_task(bot.start(BOT_TOKEN))


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8080, reload=False)
