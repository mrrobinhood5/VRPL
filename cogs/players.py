from discord.ext import commands
from discord import app_commands
from discord import Interaction

from routers.players import register_player, list_players, show_player, update_player
from classes.players import PlayerModel, UpdatePlayerModel

from fastapi.exceptions import HTTPException


class PlayerCommands(commands.GroupCog, name='players'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='register', description='Register as a Player')
    async def player_register(self, inter: Interaction, game_uid: str, calibrated_height: str) -> None:
        """/player register"""
        await inter.response.defer()
        player = PlayerModel(
            name=inter.user.name,
            discord_id=inter.user.id,
            game_uid=game_uid,
            calibrated_height=calibrated_height)
        try:
            await register_player(player)
        except HTTPException as e:
            await inter.followup.send(f'{e.detail}')
        else:
            await inter.followup.send(f'You are now Registered')

    @app_commands.command(name='update', description='Update some player data')
    async def player_update(self, inter: Interaction, name: str = None, game_uid: str = None,
                            calibrated_height: str = None, promo_email: str = None):
        """ Updates a player data"""
        await inter.response.defer()
        player = UpdatePlayerModel(name=name, game_uid=game_uid,
                                   calibrated_height=calibrated_height, promo_email=promo_email)
        try:
            await update_player(str(inter.user.id), player)
        except HTTPException as e:
            await inter.followup.send(f'{e.detail}')
        else:
            await inter.followup.send(f'Player Updated')

    @app_commands.command(name='list', description='List all Players')
    async def player_view_all(self, inter: Interaction):
        """Views all Players"""
        await inter.response.defer()
        players = await list_players()
        players = [player['name'] for player in players]
        await inter.followup.send(f'{players}')

    @app_commands.command(name='me', description='View your own data')
    async def player_me(self, inter: Interaction):
        """ Displays your own player """
        await inter.response.defer()
        me = await show_player(str(inter.user.id))
        await inter.followup.send(f'{me}')

    @app_commands.command(name='search', description='Search for a player by name')
    async def player_search(self, inter: Interaction, name: str):
        """ Searches for a Player or Players """
        await inter.response.defer()
        players = await list_players()
        players = [player for player in players if name.lower() in player['name'].lower()]
        await inter.followup.send(f'{players}')


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCommands(bot))
