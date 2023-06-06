import logging

from typing import Union

from discord.ext import commands
from discord.ui import View
from discord import app_commands, Interaction

from routers.players import register_player, list_players, show_player, update_player
from classes.players import PlayerModel, UpdatePlayerModel, PlayerEmbed, PlayerCarousel, OwnPlayerView, SelfPlayerEmbed
from classes.errors import GenericErrorEmbed

from fastapi.exceptions import HTTPException


async def process_player_update(inter: Interaction, view: Union[OwnPlayerView, PlayerCarousel]):
    try:
        await update_player(str(inter.user.id), UpdatePlayerModel(**view.updated_player))
    except HTTPException as e:
        channel = inter.channel
        await inter.client.get_channel(channel.id).send(embed=GenericErrorEmbed(inter.user, e))


class PlayerCommands(commands.GroupCog, name='players'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='register', description='Register as a Player')
    async def player_register(self, inter: Interaction, game_uid: str, calibrated_height: str) -> None:
        """ Register a Player """
        await inter.response.defer()
        player = PlayerModel(name=inter.user.name, discord_id=str(inter.user.id), game_uid=game_uid,
                             calibrated_height=calibrated_height)
        try:
            await register_player(player)
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))
        me = PlayerModel(**await show_player(str(inter.user.id)))
        me.discord_user = inter.user
        view = OwnPlayerView(me)
        await inter.followup.send(content='Registration Complete', embed=PlayerEmbed(me), view=view)

        await view.wait()
        await process_player_update(inter, view) if view.updated_player else 0

    @app_commands.command(name='list', description='List all Players')
    async def player_view_all(self, inter: Interaction) -> None:
        """Views all Players"""
        await inter.response.defer()
        players = await list_players()
        for player in players:
            user = inter.client.get_user(int(player['discord_id']))
            player['discord_user'] = user
        players = [PlayerModel(**player) for player in players]
        view = PlayerCarousel(players)
        await inter.followup.send(embed=PlayerEmbed(players[0]), view=view)

        await view.wait()
        await process_player_update(inter, view) if view.updated_player else 0

    @app_commands.command(name='me', description='View your own data')
    async def player_me(self, inter: Interaction):
        """ Displays your own player """
        await inter.response.defer(ephemeral=True)
        try:
            me = await show_player(str(inter.user.id))
            me = PlayerModel(**me)
            me.discord_user = inter.user
            view = OwnPlayerView(me)
            await inter.followup.send(embed=SelfPlayerEmbed(me), view=view)

            await view.wait()
            await process_player_update(inter, view) if view.updated_player else 0

        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

    @app_commands.command(name='search', description='Search for a player by name')
    async def player_search(self, inter: Interaction, name: str):
        """ Searches for a Player or Players """
        await inter.response.defer()
        player_list = [player for player in await list_players() if name.lower() in player['name'].lower()]
        players = []
        for player in player_list:
            p = PlayerModel(**player)
            p.discord_user = inter.client.get_user(int(p.discord_id))
            players.append(p)

        if not players:
            await inter.followup.send(f'No results found')
        else:
            view = PlayerCarousel(players)
            await inter.followup.send(embed=PlayerEmbed(players[0]), view=view)
            await view.wait()
            await process_player_update(inter, view) if view.updated_player else 0


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCommands(bot))
