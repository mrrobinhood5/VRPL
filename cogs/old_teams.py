import discord
from discord import Interaction, app_commands
from discord.ext import commands
from old_models.teams import TeamModel
from old_models.players import PlayerModel
import old_models

# from views.teamplayers import TeamCarousel, OwnTeamPlayerView, OwnTeamCoCaptainView, OwnTeamCaptainView



# async def team_view_handler(inter: Interaction, team_list: list):
#     if team_list:
#         all_teams = [FullTeamModel(**team) for team in team_list]
#         view = TeamCarousel(all_teams)
#         await inter.followup.send(embed=FullTeamEmbed(all_teams[0]), view=view)
#     else:
#         await inter.followup.send(f'No teams found')
#         return
#     await view.wait()


class TeamCommands(commands.GroupCog, name='teams'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def cog_app_command_error(self, inter: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await inter.edit_original_response(content=f'App Command Error \n {error}')

    @app_commands.command(name='list', description='List all teams')
    async def teams_view_all(self, inter: Interaction):
        """ List all teams """
        await inter.response.defer(ephemeral=True)
        if not (teams := TeamModel.get_all()):
            raise ValueError('No Teams Found')
        view = TeamModel.TeamCarousel(teams)
        await inter.followup.send(embed=teams[0].public_embed(), view=view)
        await view.wait()

    @app_commands.command(name='search', description='Search for a team')
    async def team_search(self, inter: Interaction, name: str):
        """ Search for a team """
        await inter.response.defer(ephemeral=True)
        if not (teams := TeamModel.get_some(name, 'name')):
            raise ValueError('No Teams Found')
        view = TeamModel.TeamCarousel(teams)
        await inter.followup.send(embed=teams[0].public_embed(), view=view)
        await view.wait()

    @app_commands.command(name='my_team', description='Display my team')
    async def team_me(self, inter: Interaction):
        """ Display your own team """
        await inter.response.defer(ephemeral=True)
        # check to see if you are registered
        if not (player := PlayerModel.get_by_discord(inter.user)):
            raise ValueError(f'You are not registered yet.')
        if not (approval := old_models.PlayerTeamLinkModel.get_approved(inter.user)):
            raise ValueError(f'You dont belong to a team')

        team = TeamModel.get_by_id(approval.team.id)

        match player:
            case team.captain:
                view = team.CaptainView(team)
            case team.co_captain:
                view = team.CoCaptainView(team)
            case _:
                view = team.PlayerView(team)

        await inter.followup.send(embed=team.private_embed(), view=view)
        await view.wait()
        await inter.edit_original_response(content=f'Updated')


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamCommands(bot))
