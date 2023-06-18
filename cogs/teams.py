from discord.ext import commands
from discord import app_commands, Interaction


from fastapi.exceptions import HTTPException

from routers.teams import list_teams, update_team, show_team
from routers.players import show_player, get_player_team
from routers.admin import set_settings

from models.teams import UpdateTeamModel
from models.settings import SettingsModel

from views.teamplayers import TeamCarousel, OwnTeamView
from views.teams import TeamRegisterPersistent
from models.teamplayers import FullTeamModel
from embeds.teamplayers import FullTeamEmbed,  OwnTeamEmbed
from embeds.teams import TeamRegisterEmbed


from models.errors import GenericErrorEmbed


async def process_team_update(inter: Interaction, team_id: str, team: UpdateTeamModel):
    """ helper function to send updates of teams """
    try:
        await update_team(team_id, team)
    except HTTPException as e:
        channel = inter.channel
        await inter.client.get_channel(channel.id).send(embed=GenericErrorEmbed(inter.user, e))


class TeamCommands(commands.GroupCog, name='teams'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def team_view_handler(self, inter: Interaction, team_list: list):
        if team_list:
            all_teams = [FullTeamModel(**team) for team in team_list]
            view = TeamCarousel(all_teams)
            await inter.followup.send(embed=FullTeamEmbed(all_teams[0]), view=view)
        else:
            await inter.followup.send(f'No teams found')
            return

        await view.wait()

        # TODO: this part shouldnt be here on the cog
        await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0
        updated_team = FullTeamModel(**await show_team(str(view.team.id), full=True))
        await view.msg_for_embed.edit(content=f'', embed=FullTeamEmbed(updated_team))
        #TODO: still have to get the view to send persistent embed back to bottom

    @app_commands.command(name='list', description='List all teams')
    async def teams_view_all(self, inter: Interaction):
        """ List all teams """
        await inter.response.defer(ephemeral=True)
        team_list = await list_teams(50, full=True)
        await self.team_view_handler(inter, team_list)

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction, name: str):
        """ Search for a team """
        await inter.response.defer(ephemeral=True)
        team_list = await list_teams(50, full=True)
        team_list = [team for team in team_list if name.lower() in team['name'].lower()]
        await self.team_view_handler(inter, team_list)

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your own team """
        await inter.response.defer(ephemeral=True)
        if not (_ := await show_player(player_id=str(inter.user.id))):
            await inter.followup.send(f'You are not registered yet')

        try:
            team = await get_player_team(_['_id'])
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))
            return

        full_team = FullTeamModel(**await show_team(team.get('_id'), full=True))
        view = OwnTeamView(full_team)
        await inter.followup.send(embed=OwnTeamEmbed(full_team), view=view)
        await view.wait()

        # TODO: This wants to process team edits, but shouldnt run with any other buttons.
        # await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0
        # updated_team = FullTeamModel(**await show_team(str(view.team.id), full=True))
        # await view.msg_for_embed.edit(content=f'', embed=FullTeamEmbed(updated_team))

        # TODO: this is repetitive, and there needs to be a better way to do settings
        # settings: SettingsModel = inter.client.server_config
        # old_message = await inter.channel.fetch_message(settings.teams_message)
        # await old_message.delete()
        # message = await inter.channel.send(embed=TeamRegisterEmbed(), view=TeamRegisterPersistent())
        # settings.players_message = message.id
        # await set_settings(settings)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))
