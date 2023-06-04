from discord.ext import commands
from discord.ext.commands import Context, Greedy
from discord import Object, HTTPException, app_commands, Interaction
from typing import Optional, Literal
from routers.admin import drop_db


async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner


# async def is_bot_owner(ctx):
#     return ctx.author.id == ctx.bot.owner_id


class AdminCommands(commands.Cog, name='Admin Commands'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='drop_db')
    @commands.is_owner()
    async def drop_db(self, ctx: Context):
        await drop_db()
        await ctx.reply(content='Dropped all the DBs, your honor.')

    @app_commands.command(name='purge')
    @commands.check(is_server_owner)
    async def clear_channel(self, inter: Interaction, amount: int = 100):
        deleted = await inter.channel.purge(limit=amount, reason='Owner Purge', bulk=True)
        await inter.response.defer()
        await inter.followup.send(f'{inter.user.mention} requested `{amount}` messages deleted and `{len(deleted)}` '
                                  f'were actually deleted. **I can only do 100 at a time** \n '
                                  f'If you need more, please re-run the command. ')

    @commands.command(name='get_ids')
    @commands.is_owner()
    async def get_ids(self, ctx: Context):
        ids = [member.id for member in ctx.guild.members if not member.bot]
        print(ids)

    @commands.command(name='sync')
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
