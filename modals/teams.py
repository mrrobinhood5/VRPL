from discord.ui import Modal, TextInput, View
from discord import Interaction
from models.players import PlayerModel
from models.teams import TeamModel, UpdateTeamModel


# TODO inherit both TeamRegisterModal and PlayerRegisterModal
class TeamRegisterModal(Modal, title='Register a Team'):
    team_name = TextInput(label='Team Name', custom_id='name', placeholder='New Team Name', required=True)
    team_motto = TextInput(label='Team Motto', custom_id='team_motto', placeholder='Team Motto', required=True)
    team_logo = TextInput(label='Team Logo URL', custom_id='team_logo', placeholder='URL for Team Image',
                          required=False, default=None)

    def __init__(self, view: View, captain: PlayerModel):
        super().__init__()
        self.view = view
        self.captain = captain

    async def on_submit(self, inter: Interaction) -> None:
        new_team = {
            "name": self.team_name.value,
            "team_motto": self.team_motto.value,
            "team_logo": self.team_logo.value or None,
            "captain": str(self.captain.id)
        }
        self.view.updated_team = TeamModel(**new_team)
        await inter.response.send_message(f'Registration Sent!', ephemeral=True)
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception) -> None:
        await inter.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)


class TeamUpdateModal(Modal, title='Team Update'):
    name = TextInput(label='Name', custom_id='name', placeholder='New Name', required=False)
    motto = TextInput(label='Team Motto', custom_id='team_motto', placeholder='New Team Motto', required=False)
    logo = TextInput(label='Team Logo', custom_id='team_logo', placeholder='New Team Logo', required=False)

    def __init__(self, view: View) -> None:
        super().__init__()
        self.view = view

    async def on_submit(self, inter: Interaction) -> None:
        # await inter.response.defer()
        updated_team = {
            "name": self.name.value or None,
            "team_motto": self.motto.value or None,
            "team_logo": self.logo.value or None,
        }
        self.view.updated_item = UpdateTeamModel(**updated_team)
        await inter.response.send_message(f'Updates have been sent', delete_after=10)
        # self.view.msg_for_embed = msg
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception) -> None:
        await inter.response.send_message('Oops! Something went wrong', ephemeral=True)
