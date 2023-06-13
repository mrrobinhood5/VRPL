from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle, SelectOption
from discord.ui import View, button, Button

from fastapi.exceptions import HTTPException

from routers.teams import register_team, list_teams, get_team_members, update_team, request_to_join_team, show_team
from routers.players import show_player, get_player_team

from models.teams import TeamModel, UpdateTeamModel
from modals.teams import TeamRegisterModal
from views.teams import TeamChooseView
from views.teamplayers import TeamCarousel, OwnTeamView
from models.teamplayers import FullTeamModel
from embeds.teamplayers import FullTeamEmbed,  OwnTeamEmbed, NewTeamEmbed
from models.players import PlayerModel, PlayerTeamModel

from models.errors import GenericErrorEmbed
from typing import Optional





# async def build_full_team(team: TeamModel) -> FullTeamModel:
#     """ helper function to get a full team model, to include captain, co captain and players as objects """
#     team_captain = PlayerModel(**await show_player(str(team.captain)))
#     if team.co_captain:
#         team_co_captain = PlayerModel(**await show_player(str(team.co_captain)))
#     else:
#         team_co_captain = None
#     team_members = [PlayerModel(**player) for player in await get_team_members(str(team.id))]
#
#     full_team = {**team.dict(), **{
#         "captain": team_captain,
#         "co_captain": team_co_captain,
#         "members": team_members
#     }}
#     return FullTeamModel(**full_team)


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
        await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0

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

        full_team = await show_team(team.get('_id'))
        view = OwnTeamView(full_team)
        await inter.followup.send(embed=OwnTeamEmbed(full_team), view=view)

        await view.wait()
        await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0



async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))
