from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle, SelectOption
from discord.ui import View, button, Button

from fastapi.exceptions import HTTPException

from routers.teams import register_team, list_teams, get_team_members, update_team, request_to_join_team
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


class TeamRegisterPersistent(View):
    """ This is the main View for the Team registration and Joins """
    def __init__(self):
        super().__init__(timeout=None)
        self.updated_team: Optional[TeamModel] = None

    @button(label='Register a Team', style=ButtonStyle.green, custom_id='team:register')
    async def register(self, inter: Interaction, button: Button):
        try:
            captain = await show_player(str(inter.user.id))
        except HTTPException as e:
            channel = inter.channel.id
            await inter.client.get_channel(channel).send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)

        modal = TeamRegisterModal(view=self, captain=PlayerModel(**captain))
        await inter.response.send_modal(modal)
        await modal.wait()

        channel = inter.channel.id
        try:
            await register_team(self.updated_team)
            self.updated_team = await build_full_team(self.updated_team)
            await inter.client.get_channel(channel).send(content="**New Team Registered**",
                                                         embed=NewTeamEmbed(self.updated_team))
        except HTTPException as e:
            await inter.client.get_channel(channel).send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)

    @button(label="Join a Team", style=ButtonStyle.blurple, custom_id='team:join')
    async def join(self, inter: Interaction, button: Button):
        try:  # check to see if you are registered
            player = await show_player(str(inter.user.id))
        except HTTPException as e:
            await inter.response.channel.send(embed=GenericErrorEmbed(inter.user, e))
        else:
            try:  # check to see if this player does not already belong to a team
                player_team = await get_player_team(str(inter.user.id))
            except HTTPException as e:  # doesn't belong to team
                teams = await list_teams()
                teams = [TeamModel(**team) for team in teams]
                options = [SelectOption(label=team.name, value=f'{str(team.id)}:{team.name}',
                                        description=team.team_motto)
                           for team in teams if team.active]
                view = TeamChooseView(options=options)
                await inter.response.send_message(content='Where do you want to send your request?', view=view,
                                                  ephemeral=True)
                await view.wait()
                try:
                    await request_to_join_team(view.team_value[0], PlayerTeamModel(**{"player": player['_id']}))
                except HTTPException as e:  # will error out if a similar request has been submitted
                    inter.channel.send(embed=GenericErrorEmbed(inter.user, e))
            else:  # player already belongs to team
                await inter.response.send_message(content=f'You already belong to {player_team["name"]}',
                                                  ephemeral=True)


async def build_full_team(team: TeamModel) -> FullTeamModel:
    """ helper function to get a full team model, to include captain, co captain and players as objects """
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

    @app_commands.command(name='list', description='List all teams')
    async def teams_view_all(self, inter: Interaction):
        """ List all teams """
        await inter.response.defer(ephemeral=True)
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
        await inter.response.defer(ephemeral=True)
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
        """ Display your own team """
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
