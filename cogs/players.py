import logging

from discord.ext import commands
from discord import app_commands
from discord import Interaction

from routers.players import register_player, list_players, show_player, update_player
from classes.players import PlayerModel, UpdatePlayerModel, PlayerEmbed, PlayerCarousel, OwnPlayerView
from classes.errors import GenericErrorEmbed

from fastapi.exceptions import HTTPException


class PlayerCommands(commands.GroupCog, name='players'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='register', description='Register as a Player')
    async def player_register(self, inter: Interaction, game_uid: str, calibrated_height: str) -> None:
        """ Register a Player """
        await inter.response.defer()
        player = PlayerModel(name=inter.user.name, discord_id=inter.user.id, game_uid=game_uid,
                             calibrated_height=calibrated_height)
        try:
            await register_player(player)
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))
        else:
            me = await show_player(str(inter.user.id))
            me = PlayerModel(**me)
            embed = PlayerEmbed(me, inter.user)
            view = OwnPlayerView(me, inter.user)
            await inter.followup.send(content='Registration Complete', embed=embed, view=view)
            await view.wait()
            if view.updated_player:
                try:
                    await update_player(str(inter.user.id), UpdatePlayerModel(**view.updated_player))
                except HTTPException as e:
                    logging.info(msg=e)

    @app_commands.command(name='list', description='List all Players')
    async def player_view_all(self, inter: Interaction):
        """Views all Players"""
        await inter.response.defer()
        players = await list_players()
        players = [(PlayerModel(**player), inter.client.get_user(int(player['discord_id']))) for player in players]
        view = PlayerCarousel(players)
        await inter.followup.send(embed=PlayerEmbed(players[0][0], players[0][1]), view=view)
        await view.wait()
        if view.updated_player:
            try:
                await update_player(str(inter.user.id), UpdatePlayerModel(**view.updated_player))
            except HTTPException as e:
                logging.info(msg=e)

    @app_commands.command(name='me', description='View your own data')
    async def player_me(self, inter: Interaction):
        """ Displays your own player """
        await inter.response.defer()
        try:
            me = await show_player(str(inter.user.id))
            me = PlayerModel(**me)
            view = OwnPlayerView(me, inter.user)
            await inter.followup.send(embed=PlayerEmbed(me, inter.user), view=view)
            await view.wait()
            if view.updated_player:
                try:
                    await update_player(str(inter.user.id), UpdatePlayerModel(**view.updated_player))
                except HTTPException as e:
                    logging.info(msg=e)

        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

    @app_commands.command(name='search', description='Search for a player by name')
    async def player_search(self, inter: Interaction, name: str):
        """ Searches for a Player or Players """
        await inter.response.defer()
        players = await list_players()
        players = [(PlayerModel(**player), inter.client.get_user(int(player['discord_id'])))
                   for player in players if name.lower() in player['name'].lower()]
        if not players:
            await inter.followup.send(f'No results found')
        else:
            await inter.followup.send(embed=PlayerEmbed(players[0][0], players[0][1]), view=PlayerCarousel(players))


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCommands(bot))
