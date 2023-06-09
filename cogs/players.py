import logging

from typing import Union

import discord
from discord.ext import commands
from discord.ui import View, Button, button
from discord import app_commands, Interaction, Embed

from routers.players import register_player, list_players, show_player, update_player
from classes.players import PlayerModel, UpdatePlayerModel, PlayerEmbed, PlayerCarousel, OwnPlayerView, SelfPlayerEmbed
from classes.players import PlayerRegisterModal
from classes.errors import GenericErrorEmbed

from fastapi.exceptions import HTTPException

class PlayerRegisterPersistent(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.updated_player: PlayerModel = None

    @button(label='Register a Player', style=discord.ButtonStyle.green, custom_id='player:register')
    async def register(self, inter: Interaction, button: Button):
        modal = PlayerRegisterModal(view=self)
        await inter.response.send_modal(modal)
        await modal.wait()

        channel = inter.channel.id
        try:
            await register_player(self.updated_player)
            self.updated_player.discord_user = inter.user
            await inter.client.get_channel(channel).send(embed=PlayerEmbed(self.updated_player))
        except HTTPException as e:
            await inter.client.get_channel(channel).send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)


async def process_player_update(inter: Interaction, player: UpdatePlayerModel):
    try:
        await update_player(str(inter.user.id), player)
    except HTTPException as e:
        channel = inter.channel
        await inter.client.get_channel(channel.id).send(embed=GenericErrorEmbed(inter.user, e))


class PlayerCommands(commands.GroupCog, name='players'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    # @app_commands.command(name='register', description='Register as a Player')
    # async def player_register(self, inter: Interaction, game_uid: str, calibrated_height: str) -> None:
    #     """ Register a Player """
    #     await inter.response.defer()
    #     player = PlayerModel(name=inter.user.name, discord_id=str(inter.user.id), game_uid=game_uid,
    #                          calibrated_height=calibrated_height)
    #     try:
    #         await register_player(player)
    #     except HTTPException as e:
    #         await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))
    #     me = PlayerModel(**await show_player(str(inter.user.id)))
    #     me.discord_user = inter.user
    #     view = OwnPlayerView(me)
    #     await inter.followup.send(content='Registration Complete', embed=PlayerEmbed(me), view=view)
    #
    #     await view.wait()
    #     await process_player_update(inter, view) if view.updated_player else 0

    @app_commands.command(name='list', description='List all Players')
    async def player_view_all(self, inter: Interaction) -> None:
        """Views all Players"""
        await inter.response.defer(ephemeral=True)
        players = await list_players()
        for player in players:
            user = inter.client.get_user(int(player['discord_id']))
            player['discord_user'] = user
        players = [PlayerModel(**player) for player in players]
        view = PlayerCarousel(players)
        await inter.followup.send(embed=PlayerEmbed(players[0]), view=view)

        await view.wait()
        await process_player_update(inter, view.updated_player) if view.updated_player else 0

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
            await process_player_update(inter, view.updated_player) if view.updated_player else 0

        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

    @app_commands.command(name='search', description='Search for a player by name')
    async def player_search(self, inter: Interaction, name: str):
        """ Searches for a Player or Players """
        await inter.response.defer(ephemeral=True)
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
            await process_player_update(inter, view.updated_player) if view.updated_player else 0


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCommands(bot))
