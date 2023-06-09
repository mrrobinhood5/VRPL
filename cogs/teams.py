from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle, SelectOption
from discord.ui import View, button, Button, Select


from fastapi.exceptions import HTTPException

from routers.teams import register_team, list_teams, get_team_members, update_team
from routers.players import show_player, get_player_team

from classes.teams import TeamModel, UpdateTeamModel, TeamRegisterModal, TeamJoinModal
from classes.team_player_mix import FullTeamModel, FullTeamEmbed, TeamCarousel, OwnTeamView, OwnTeamEmbed, NewTeamEmbed
from classes.players import PlayerModel

from classes.errors import GenericErrorEmbed
import json


class TeamRegisterPersistent(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.updated_team: TeamModel = None

    @button(label='Register a Team', style=ButtonStyle.green, custom_id='team:register')
    async def register(self, inter: Interaction, button: Button):
        captain = await show_player(str(inter.user.id))
        modal = TeamRegisterModal(view=self, captain=PlayerModel(**captain))
        await inter.response.send_modal(modal)
        await modal.wait()

        channel = inter.channel.id
        try:
            await register_team(self.updated_team)
            # self.updated_team.discord_user = inter.user
            self.updated_team = await build_full_team(self.updated_team)
            await inter.client.get_channel(channel).send(embed=NewTeamEmbed(self.updated_team))
        except HTTPException as e:
            await inter.client.get_channel(channel).send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)

class TeamChooseDropdown(Select):
    def __init__(self):
        super().__init__(placeholder='Choose a Team', min_values=1, max_values=1)


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


    #TODO: does this become obsolete if using single embed?
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

    @app_commands.command(name='join', description='Request to Join a Team')
    async def join_team(self, inter: Interaction):
        """ Request to join a team """

        # await inter.response.defer(ephemeral=True)
        dropdown = TeamChooseDropdown()
        teams = await list_teams()
        teams = [TeamModel(**team) for team in teams]
        for team in teams:
            if team.active:
                dropdown.append_option(SelectOption(label=team.name, value=str(team.id), description=team.team_motto))

        team_join = TeamJoinModal()
        team_join.add_item(dropdown)
        await inter.response.send_modal(team_join) # TODO: I left of here, cannot send a dropdown in a modal, needs a view
        await team_join.wait()
        await inter.followup.send(f'Request Sent')
        # check if User is registered


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))
