from fastapi.exceptions import HTTPException

from discord.ext import commands
from discord import app_commands, Interaction

from embeds.players import PlayerEmbed, SelfPlayerEmbed, PlayerRegisterEmbed
from routers.players import list_players, show_player, update_player
from routers.admin import set_settings
from models.players import PlayerModel, UpdatePlayerModel
from models.errors import GenericErrorEmbed
from models.settings import SettingsModel
from views.players import PlayerCarousel, OwnPlayerView, PlayerRegisterPersistent


# async def process_player_update(inter: Interaction, player: UpdatePlayerModel):
#     """ Helper function to process any player updates """
#     try:
#         await update_player(str(inter.user.id), player)
#     except HTTPException as e:
#         channel = inter.channel
#         await inter.client.get_channel(channel.id).send(embed=GenericErrorEmbed(inter.user, e))


class PlayerCommands(commands.GroupCog, name='players'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='list', description='List all Players')
    async def player_view_all(self, inter: Interaction) -> None:
        """ Views all Players """
        await inter.response.defer(ephemeral=True)
        players = await list_players()
        for player in players:
            user = inter.client.get_user(int(player['discord_id']))
            player['discord_user'] = user
        players = [PlayerModel(**player) for player in players]
        view = PlayerCarousel(players)
        await inter.followup.send(embed=PlayerEmbed(players[0]), view=view)

        await view.wait()
        # await process_player_update(inter, view.updated_player) if view.updated_player else 0

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

            # TODO: maybe put this in a daily loop
            # settings: SettingsModel = inter.client.server_config
            # old_message = await inter.channel.fetch_message(settings.players_message)
            # await old_message.delete()
            # message = await inter.channel.send(embed=PlayerRegisterEmbed(), view=PlayerRegisterPersistent())
            # settings.players_message = message.id
            # await set_settings(settings)


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
            # await process_player_update(inter, view.updated_player) if view.updated_player else 0


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCommands(bot))
