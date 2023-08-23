from typing import Optional, Literal

from discord.ext import commands
from discord.ext.commands import Context, Greedy
from discord import Object, HTTPException, app_commands, Interaction, TextChannel
from old_models.teams import TeamRegisterPersistent
from old_models.players import PlayerRegisterPersistent
from old_models.admin import SettingsModel


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
        settings = inter.client.settings
        await settings.get_messages()

        if channel == 'Player':
            if settings.players_message:
                try:
                    await settings.players_message.delete()
                except Exception as e:
                    print(e)
            settings.players_channel_id = select.id
            settings.players_channel = select
            persistent = PlayerRegisterPersistent()
            settings.players_message = await select.send(embed=persistent.embed(), view=persistent)
            settings.players_message_id = settings.players_message.id

        if channel == 'Team':
            if settings.teams_message:
                try:
                    await settings.teams_message.delete()
                except Exception as e:
                    print(e)
            settings.teams_channel_id = select.id
            settings.teams_channel = select
            persistent = TeamRegisterPersistent()
            settings.teams_message = await select.send(embed=persistent.embed(), view=persistent)
            settings.teams_message_id = settings.teams_message.id

        settings.save()
        inter.client.refresh_settings()

    @commands.command(name='drop_db')
    @commands.is_owner()
    async def drop_db(self, ctx: Context):
        for collection in ctx.bot.db.list_collections:
            collection.drop()
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
