from discord.ext import commands
from discord.ext.commands import Context, Greedy
from typing import Optional, Literal
from discord import Object, HTTPException, app_commands, Interaction, TextChannel


async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner


class AdminCommands(commands.Cog, name='Admin Commands'):

    def __init__(self, bot):
        self.bot = bot

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

    @app_commands.command(name='dashboard', description='Displays the AdminDashboard')
    @commands.is_owner()
    @app_commands.default_permissions(administrator=True)
    async def dashboard(self, inter: Interaction):
        """ Defines a Channel for the persistent Embed """
        dash = inter.client.admin_engine.get_dashboard()
        embed = dash.embed(private=True)
        await inter.response.send_message(embed=embed, view=dash, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
