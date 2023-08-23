from discord.ext import commands
from discord import app_commands, Interaction

from old_models.players import PlayerModel

from pydantic import ValidationError


class PlayerCommands(commands.GroupCog, name='players'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='me', description='View your own data')
    async def player_me(self, inter: Interaction):
        """ Displays your own player """
        await inter.response.defer(ephemeral=True)
        try:
            me = PlayerModel.get_by_discord(inter.user)
        except ValueError as e:
            await inter.followup.send(f'{e}')
            return
        view = PlayerModel.PlayerView([me])
        await inter.followup.send(embed=me.private_embed(), view=view)
        await view.wait()

    @app_commands.command(name='list', description='List all Players')
    async def player_view_all(self, inter: Interaction) -> None:
        """ Views all Players """
        await inter.response.defer(ephemeral=True)
        if not (players := PlayerModel.get_all()):
            raise ValueError('No Players')

        view = PlayerModel.PlayerCarousel(players)
        await inter.followup.send(embed=players[0].public_embed(), view=view)
        await view.wait()

    @app_commands.command(name='search', description='Search for a player by name')
    async def player_search(self, inter: Interaction, name: str):
        """ Searches for a Player or Players """
        await inter.response.defer(ephemeral=True)

        players = PlayerModel.get_some(search=name, key='name')
        if not players:
            await inter.followup.send(f'No results found')
        else:
            view = PlayerModel.PlayerCarousel(players)
            await inter.followup.send(embed=players[0].public_embed(), view=view)
            await view.wait()


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCommands(bot))
