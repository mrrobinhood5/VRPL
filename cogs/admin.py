import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy
from typing import Optional, Literal, TypeVar
from discord import Object, HTTPException, app_commands, Interaction

from models import *


# GameEnum = TypeVar('GameEnum', bound=await )
class TimeConverter(app_commands.Transformer):
    async def transform(self, inter: Interaction, value: str) -> datetime:
        formats = ['%m/%d/%y', '%m/%d/%Y']
        for format in formats:
            try:
                result = datetime.strptime(value, format)
                return result
            except ValueError:
                pass
        raise ValueError('Not a Proper Time Format')


async def is_server_owner(ctx):
    return ctx.author == ctx.guild.owner


async def send_not_found(ctx):
    await ctx.followup.send(content='None Found')


class AdminCommands(commands.Cog, name='admin'):

    def __init__(self, bot):
        print('AdminCommands Cog loaded')
        self.bot = bot
        super().__init__()

    async def cog_command_error(self, inter: Interaction, error):
        print(f'Cog CommandError Called with {error}')

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
    async def find_player(self, inter: Interaction, search_type: SearchType,
                          name: Optional[str], member: Optional[discord.Member],
                          game: Optional[str], location: Optional[str],
                          captain: Optional[bool], co_captain: Optional[bool],
                          suspended: Optional[bool] = False, banned: Optional[bool] = False):
        """ Searches for a Player, inline mode """
        await inter.response.defer()

        if game:
            game = await inter.client.ge.get_one_by_name(game)
        if location:
            location = [x for x in Location if x.value == location][0]

        search = {'game': game, 'location': location, 'banned': banned, 'suspended': suspended,
                  'captain': captain, 'co_captain': co_captain, 'name': name, 'member': member}

        match search_type:
            case SearchType.ByName:
                if not name:
                    return await inter.followup.send(content='You need to input a name')
                search.update({'name': name})
            case SearchType.ByDiscord:
                return await inter.followup.send(content='You need to choose a member') if not member else 0
                search.update({'member': member.id})
        if result := await inter.client.pe.get_by(**search):
            return await inter.followup.send(content=[x.name for x in result])
        else:
            return await inter.followup.send(content='Nothing found')

    @app_commands.command(name='find_player_new', description='Search for a specific player, Dashboard Type')
    @app_commands.default_permissions(administrator=True)
    async def find_player_new(self, inter: Interaction, search_type: SearchType):
        await inter.response.defer()

        class PlayerSearchView(discord.ui.View):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self):
                for child in view.children:
                    if child.values:
                        continue
                    else:
                        return
                self.stop()

        class SelectMenu(discord.ui.Select):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def callback(self, inter: Interaction) -> Any:
                if len(self.options) >= len(self.values):
                    await self.view.callback()

        # first we need to know what type of search this will be
        select_menu = SelectMenu(placeholder='What type of filters')
        select_menu.add_option(label='Game', value='game')
        select_menu.add_option(label='Location', value='location')
        select_menu.add_option(label='Captain', value='captain')
        select_menu.add_option(label='CoCaptain', value='co_captain')
        select_menu.add_option(label='Suspended', value='suspended')
        select_menu.add_option(label='Banned', value='banned')
        select_menu.max_values = len(select_menu.options)
        view = PlayerSearchView().add_item(select_menu)
        action_msg = await inter.followup.send(content='Select Filters for search', view=view)
        await view.wait()
        view.clear_items()

        menus = []
        if select_menu.values:
            for filter in select_menu.values:
                match filter:
                    case 'game':
                        game_menu = SelectMenu(placeholder='Filter Games')
                        menus.append(game_menu)
                        games = await inter.client.ge.get_by(output=SearchOutputType.OnlyNames)
                        for game in games:
                            game_menu.add_option(value=game.name, label=game.name)

                    case 'location':
                        location_menu = SelectMenu(placeholder='Filter Locations')
                        menus.append(location_menu)
                        locations = await inter.client.pe.all_player_locations()
                        print(len(locations))
                        for location in locations:
                            location_menu.add_option(value=location.name, label=location.name)

        for menu in menus:
            view.add_item(menu)
        await action_msg.edit(content='', view=view)
        await view.wait()

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
    @app_commands.describe(registered_on='Format is MM/DD/YY')
    async def make_player(self, inter: Interaction, game: str, member: discord.Member, name: str,
                          game_uid: Optional[str], registered_on: Optional[TimeConverter],
                          height: Optional[float], location: Location, promo_email: Optional[str]):
        """ Manually makes a player by admin """
        await inter.response.defer()
        registered_on = datetime.now() if not registered_on else registered_on
        game = await inter.client.ge.get_one_by_name(game)
        player = await inter.client.pe.register_player(game=game, discord_id=member.id, name=name, game_uid=game_uid,
                                                       height=height, location=location, promo_email=promo_email,
                                                       registered_on=registered_on)
        await inter.followup.send(content=f'Player Created: {player} ')

    @app_commands.command(name='promote_player', description='Update Player Type')
    @app_commands.default_permissions(administrator=True)
    async def promote_player(self, inter: Interaction, team: str, player: str):
        pass

    @app_commands.command(name='dashboard', description='Show Admin Dash')
    @app_commands.default_permissions(administrator=True)
    async def admin_dash(self, inter: Interaction):
        await inter.response.defer()

        # crates the Admin Dash
        view = await inter.client.ae.dashboard()
        msg = await inter.followup.send(content=view.text, embeds=view.embeds, view=view)
        view.msg = msg
        print(f'On view: {view}, awaiting')
        await view.wait()

        # follows up until there's no view.next with the Done or Prev Buttons
        while view.next:
            print(f'returned from: {view}, type: {type(view)}, going to {view.next}')
            view = await view.next  # this is a function
            msg = await view.msg.edit(content=view.text, embeds=view.embeds, view=view)
            view.msg = msg
            print(f'On view: {view}, type: {type(view)}, awaiting')
            await view.wait()

        return

    @promote_player.autocomplete('team')
    async def autocomplete_team(self, inter: Interaction, current: str):
        teams = await inter.client.te.get_by(name=current, output=SearchOutputType.OnlyNames)
        return [app_commands.Choice(name=team.name, value=team.name) for team in teams]

    @promote_player.autocomplete('player')
    async def autocomplete_players(self, inter: Interaction, current: str):
        players = await inter.client.te.aggregate(match=inter.namespace.team, target_collection='PlayerBase',
                                                  source_field='members')
        choices = [app_commands.Choice(name=player.name, value=player.name) for player in players]
        return choices

    @make_player.autocomplete('game')
    @find_player.autocomplete('game')
    async def autocomplete_games(self, inter: Interaction, current: str):
        choices = await inter.client.ge.all_games_names()
        return [app_commands.Choice(name=choice.name, value=choice.name) for choice in choices]

    @find_player.autocomplete('location')
    async def autocomplete_locations(self, inter: Interaction, current: str):
        choices = await inter.client.pe.all_player_locations()
        return [app_commands.Choice(name=choice.name, value=choice.name) for choice in choices]


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
