from discord.ext import commands
from discord import app_commands
from discord import Interaction

from fastapi.exceptions import HTTPException

from routers.teams import register_team, list_teams, get_team_members, update_team
from routers.players import show_player, get_player_team

from classes.teams import TeamModel, NewTeamEmbed, UpdateTeamModel
from classes.team_player_mix import FullTeamModel, FullTeamEmbed, TeamCarousel, OwnTeamView, OwnTeamEmbed
from classes.players import PlayerModel

from classes.errors import GenericErrorEmbed
import json


async def build_full_team(team: TeamModel) -> FullTeamModel:
    team_captain = PlayerModel(**await show_player(str(team.captain)))
    if team.co_captain:
        team_co_captain = PlayerModel(**await show_player(str(team.co_captain)))
    else:
        team_co_captain = None
    team_members = [PlayerModel(**player) for player in await get_team_members(str(team.id))]

    full_team = {**team.dict(), **{
        "captain": team_captain,
        "co_captain": team_co_captain,
        "members": team_members
    }}
    return FullTeamModel(**full_team)


async def process_team_update(inter: Interaction, team_id: str, team: UpdateTeamModel):
    try:
        await update_team(team_id, team)
    except HTTPException as e:
        channel = inter.channel
        await inter.client.get_channel(channel.id).send(embed=GenericErrorEmbed(inter.user, e))


class TeamCommands(commands.GroupCog, name='teams'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name='register', description='Register a team')
    async def team_register(self, inter: Interaction, name: str, motto: str, logo: str = None):
        """ Register a team """
        await inter.response.defer()

        try:
            captain = await show_player(str(inter.user.id))
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

        team = TeamModel(name=name, team_motto=motto, team_logo=logo, captain=captain['_id'])

        try:
            team = await register_team(team)
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))
        else:
            created_team = json.loads(team.body.decode())
            await inter.followup.send(content='Registration Complete', embed=NewTeamEmbed(inter, created_team))

    @app_commands.command(name='list', description='List all teams')
    async def teams_view_all(self, inter: Interaction):
        """ List all teams """
        await inter.response.defer()
        team_list = await list_teams(50)
        if team_list:
            all_teams = [await build_full_team(TeamModel(**team)) for team in team_list]
            view = TeamCarousel(all_teams)
            await inter.followup.send(embed=FullTeamEmbed(all_teams[0]), view=view)
        else:
            await inter.followup.send(f'No teams Found')
            return

        await view.wait()
        await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction, name: str):
        """ Search for a team """
        await inter.response.defer()
        team_list = await list_teams(50)
        team_list = [team for team in team_list if name.lower() in team['name'].lower()]
        if team_list:
            all_teams = [await build_full_team(TeamModel(**team)) for team in team_list]
            view = TeamCarousel(all_teams)
            await inter.followup.send(embed=FullTeamEmbed(all_teams[0]), view=view)
        else:
            await inter.followup.send(f'No teams found')
            return

        await view.wait()
        await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your team """
        await inter.response.defer(ephemeral=True)
        if not (_ := await show_player(player_id=str(inter.user.id))):
            await inter.followup.send(f'You are not registered yet')

        try:
            team = await get_player_team(_['_id'])
        except HTTPException as e:
            await inter.followup.send(embed=GenericErrorEmbed(inter.user, e))

        full_team = await build_full_team(TeamModel(**team))
        view = OwnTeamView(full_team)
        await inter.followup.send(embed=OwnTeamEmbed(full_team), view=view)

        await view.wait()
        await process_team_update(inter, str(view.team.id), view.updated_team) if view.updated_team else 0


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))