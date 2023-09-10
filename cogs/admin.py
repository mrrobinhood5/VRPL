import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy
from typing import Optional, Literal, TypeVar
from discord import Object, HTTPException, app_commands, Interaction

from models import *

# GameEnum = TypeVar('GameEnum', bound=await )

async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner

async def send_not_found(ctx):
    await ctx.followup.send(content='None Found')

class AdminCommands(commands.Cog, name='Admin Commands'):

    def __init__(self, bot):
        print('admin loaded')
        self.bot = bot

    async def cog_command_error(self, inter: Interaction, error):
        print(error)

    @commands.command(name='sync')
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        print('sync command envoked')
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

    @app_commands.command(name='find_player', description='Search for a specific player')
    @app_commands.default_permissions(administrator=True)
    async def find_player(self, inter: Interaction, game: str, type: PlayerSearchType,
                          discord: Optional[discord.Member], name: Optional[str]):
        """ Searches for a Player """
        await inter.response.defer()

        match type:
            case PlayerSearchType.NAME:
                if not name:
                    await inter.followup.send('You need to input a name')
                if player := await inter.client.pe.get_by_name(name):
                    await inter.followup.send(content=player.name)
                else:
                    await send_not_found(inter)
            case PlayerSearchType.DISCORD:
                if not discord:
                    await inter.followup.send('You need to choose a member')
                if player := await inter.client.pe.get_by_discord(discord.id):
                    await inter.followup.send(content=player.name)
                else:
                    await send_not_found(inter)

    @app_commands.command(name='find_players', description='Search for a many players')
    @app_commands.default_permissions(administrator=True)
    async def find_players(self, inter: Interaction, type: PlayersSearchType,
                           location: Optional[Location], alias: Optional[str]):
        """ Searches for a Players with other things """
        await inter.response.defer()

        match type:
            case PlayersSearchType.LOCATION:
                if not location:
                    await inter.followup.send('You need to input a location')
                if players := await inter.client.pe.get_by_location(location):
                    await inter.followup.send(content=[player.name for player in players])
                else:
                    await send_not_found(inter)
            case PlayersSearchType.ALIAS:
                if not alias:
                    await inter.followup.send('You need to type an alias')
                if players := await inter.client.pe.get_by_alias(alias):
                    await inter.followup.send(content=[player.name for player in players])
                else:
                    await send_not_found(inter)
            case PlayersSearchType.BANNED:
                if players := await inter.client.pe.get_banned():
                    await inter.followup.send(content=[player.name for player in players])
                else:
                    await send_not_found(inter)
            case PlayersSearchType.CAPTAINS:
                if players := await inter.client.pe.get_captains():
                    await inter.followup.send(content=[player.name for player in players])
                else:
                    await send_not_found(inter)
            case PlayersSearchType.COCAPTAINS:
                if players := await inter.client.pe.get_co_captains():
                    await inter.followup.send(content=[player.name for player in players])
                else:
                    await send_not_found(inter)
            case PlayersSearchType.SUSPENDED:
                if players := await inter.client.pe.get_co_captains():
                    await inter.followup.send(content=[player.name for player in players])
                else:
                    await send_not_found(inter)

    @app_commands.command(name='list_games', description='List all Games')
    @app_commands.default_permissions(administrator=True)
    async def get_games(self, inter: Interaction):
        await inter.response.defer()
        games = await inter.client.ge.all_games_names()
        await inter.followup.send(content=games)

    @app_commands.command(name='make_game', description='Make a new Game')
    @app_commands.default_permissions(administrator=True)
    async def create_game(self, inter: Interaction, name: str, description: Optional[str], link: Optional[str]):
        await inter.response.defer()
        game = await inter.client.ge.create_game(name=name, description=description, link=link)
        await inter.followup.send(content=game)

    @app_commands.command(name='make_player', description='Manually Create a Player')
    @app_commands.default_permissions(administrator=True)
    async def make_player(self, inter: Interaction, game: str, member: discord.Member, name: str, game_uid: Optional[str],
                          height: Optional[float], location: Location, promo_email: Optional[str]):
        """ Manually makes a player by admin """
        await inter.response.defer()
        await inter.followup.send('Fake Player made')

    @make_player.autocomplete('game')
    @find_player.autocomplete('game')
    async def autocomplete_callback(self, inter: Interaction, current: str):
        choices = await inter.client.ge.all_games_names()
        return [app_commands.Choice(name=choice.name, value=choice.name) for choice in choices]

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
