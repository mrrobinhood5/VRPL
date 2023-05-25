import asyncio
from fastapi import FastAPI
from config import BOT_TOKEN, INTENTS, BOT_PREFIX
from discord.ext import commands
from routers import players, teams, team_join_approvals
from database import db
import discord
import uvicorn

app = FastAPI()
bot = commands.Bot(command_prefix=BOT_PREFIX, description='VRPL Team Manager', intents=INTENTS)

app.include_router(players.router)
app.include_router(teams.router)
app.include_router(team_join_approvals.router)


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


@app.get("/db/drop")
async def drop_db():
    for coll in await db.list_collection_names():
        await db.drop_collection(coll)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID: {bot.user.id})')
    activity = discord.Game('Contractor$ on Quest 3')
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.command()
async def hello(ctx: commands.Context):
    """ Just says Hello"""
    await ctx.reply(f'### Well hello to you too {ctx.author.name}')


async def is_owner(ctx):
    return ctx.author == ctx.guild.owner


@bot.command(name='purge')
@commands.check(is_owner)
async def clear_channel(ctx: commands.Context, amount: int = 100):

    deleted = await ctx.channel.purge(limit=amount, reason='Owner Purge', bulk=True)
    await ctx.send(f'{ctx.author.mention} requested `{amount}` messages deleted and `{len(deleted)}` '
                   f'were actually deleted. **I can only do 100 at a time** \n '
                   f'If you need more, please re-run the command. ')


@app.on_event('startup')
async def run_bot():
    asyncio.create_task(bot.start(BOT_TOKEN))


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8080, reload=True)
