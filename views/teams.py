from typing import Optional

from fastapi.exceptions import HTTPException

from discord import SelectOption, Interaction, ButtonStyle
from discord.ui import Select, View, button, Button

from routers.players import show_player, get_player_team
from routers.teams import list_teams, register_team, request_to_join_team, show_team

from models.teamplayers import FullTeamModel
from models.teams import TeamModel
from models.players import PlayerModel, PlayerTeamModel
from models.errors import GenericErrorEmbed

from embeds.teamplayers import NewTeamEmbed

from modals.teams import TeamRegisterModal


class TeamChooseDropdown(Select):
    def __init__(self, options=list[SelectOption]):
        super().__init__(placeholder='Choose a Team', min_values=1, max_values=1, options=options)

    async def callback(self, inter: Interaction):
        self.view.team_value = self.values[0].split(':')
        await inter.response.send_message(f'`{inter.user.name}` has requested to join `{self.view.team_value[1]}`')
        self.view.stop()


class TeamChooseView(View):
    def __init__(self, options: list[SelectOption]):
        super().__init__()
        self.add_item(TeamChooseDropdown(options=options))
        self.team_value = None


class TeamRegisterPersistent(View):
    """ This is the main View for the Team registration and Joins """
    def __init__(self):
        super().__init__(timeout=None)
        self.updated_team: Optional[TeamModel] = None

    @button(label='Register a Team', style=ButtonStyle.green, custom_id='team:register')
    async def register(self, inter: Interaction, button: Button):
        try:
            captain = await show_player(inter.user.id)
        except HTTPException as e:
            await inter.channel.send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)  # "not registered" error

        modal = TeamRegisterModal(view=self, captain=PlayerModel(**captain))
        await inter.response.send_modal(modal)
        await modal.wait()

        try:
            await register_team(self.updated_team)
            self.updated_team = FullTeamModel(**await show_team(str(self.updated_team.id), full=True))
            await inter.channel.send(content="**New Team Registered**", embed=NewTeamEmbed(self.updated_team))

        except HTTPException as e:
            await inter.channel.send(embed=GenericErrorEmbed(inter.user, e), delete_after=10)

    @button(label="Join a Team", style=ButtonStyle.blurple, custom_id='team:join')
    async def join(self, inter: Interaction, button: Button):
        try:  # check to see if you are registered
            player = await show_player(inter.user.id)
        except HTTPException as e:
            await inter.response.channel.send(embed=GenericErrorEmbed(inter.user, e))
        else:
            try:  # check to see if this player does not already belong to a team
                player_team = await get_player_team(inter.user.id)
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
                view.clear_items()
                msg = await inter.original_response()
                await msg.edit(content=f'Request Sent!', view=view)
                try:
                    await request_to_join_team(view.team_value[0], PlayerTeamModel(**{"player": player['_id']}))
                except HTTPException as e:  # will error out if a similar request has been submitted
                    await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))

                # Send DM to both captain and co-captain
                team = FullTeamModel(**await show_team(view.team_value[0], full=True))
                await inter.guild.get_member(team.captain.discord_id).send(f'{inter.user.name} requested to join your team. use `/team my_team` to approve this')
                if team.co_captain:
                    await inter.guild.get_member(team.co_captain.discord_id).send(f'{inter.user.name} requested to join your team. use `/team my_team` to approve this')
            else:  # player already belongs to team
                await inter.response.send_message(content=f'You already belong to {player_team["name"]}',
                                                  ephemeral=True)