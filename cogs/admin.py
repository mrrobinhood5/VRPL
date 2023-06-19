from typing import Optional, Literal

from discord.ext import commands
from discord.ext.commands import Context, Greedy
from discord import Object, HTTPException, app_commands, Interaction, TextChannel

from embeds.players import PlayerRegisterEmbed
from embeds.teams import TeamRegisterEmbed

from routers.admin import drop_db, set_settings, get_settings

from views.teams import TeamRegisterPersistent
from views.players import PlayerRegisterPersistent

from models.settings import SettingsModel


async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner


class AdminCommands(commands.Cog, name='Admin Commands'):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='config', description='Set default channels')
    @commands.is_owner()
    @app_commands.default_permissions(administrator=True)
    async def config_channels(self, inter: Interaction, channel: Literal['Player', 'Team'], select: TextChannel):
        """ Defines a Channel for the persistent Embed """
        await inter.response.send_message(f'Request Sent', ephemeral=True)

        if settings := await get_settings():
            settings = SettingsModel(**settings)
        else:
            settings = SettingsModel(**{})
        _ = inter.client.get_channel(select.id)

        if channel == 'Player':
            settings.players_channel = select.id
            message = await _.send(embed=PlayerRegisterEmbed(), view=PlayerRegisterPersistent())
            settings.players_message = message.id
        else:
            settings.teams_channel = select.id
            message = await _.send(embed=TeamRegisterEmbed(), view=TeamRegisterPersistent())
            settings.teams_message = message.id
        await set_settings(settings)

    @commands.command(name='drop_db')
    @commands.is_owner()
    async def drop_db(self, ctx: Context):
        await drop_db()
        await ctx.reply(content='Dropped all the DBs, your honor.')

    @app_commands.command(name='purge')
    @app_commands.default_permissions(administrator=True)
    @commands.check(is_server_owner)
    async def clear_channel(self, inter: Interaction, amount: int = 100):
        await inter.response.send_message(f'Purged Channel')
        await inter.channel.purge(limit=amount, reason='Owner Purge', bulk=True)

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
