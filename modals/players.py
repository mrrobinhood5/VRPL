from discord import Interaction

from discord.ui import Modal, TextInput, View

from models.players import PlayerModel, UpdatePlayerModel


class PlayerRegisterModal(Modal, title='Register a Player'):
    game_uid = TextInput(label='UID', custom_id='game_uid', placeholder='Updated UID', required=True)
    calibrated_height = TextInput(label='Calibrated Height', custom_id='calibrated_height',
                                  placeholder='New Height', required=True)
    promo_email = TextInput(label='Promo Email', custom_id='promo_email',
                            placeholder='Email for Promos (Optional)', required=False, default=None)

    def __init__(self, view: View):
        super().__init__()
        self.view = view

    async def on_submit(self, inter: Interaction) -> None:
        new_player = {
            "name": inter.user.name,
            "discord_id": inter.user.id,
            "game_uid": self.game_uid.value,
            "calibrated_height": self.calibrated_height.value,
            "promo_email": self.promo_email.value or None
        }
        self.view.updated_player = PlayerModel(**new_player)
        await inter.response.send_message(f'Registration Sent!', ephemeral=True)
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception) -> None:
        await inter.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)


class PlayerUpdateModal(Modal, title='Player update'):
    name = TextInput(label='Name', custom_id='name', placeholder='New Name', required=False)
    game_uid = TextInput(label='UID', custom_id='game_uid', placeholder='Updated UID', required=False)
    calibrated_height = TextInput(label='Calibrated Height', custom_id='calibrated_height',
                                  placeholder='New Height', required=False)
    promo_email = TextInput(label='Promo Email', custom_id='promo_email',
                            placeholder='Email for Promos', required=False, )

    def __init__(self, view: View):
        super().__init__()
        self.view = view

    async def on_submit(self, inter: Interaction) -> None:
        updated_player = {
            "name": self.name.value or None,
            "game_uid": self.game_uid.value or None,
            "calibrated_height": self.calibrated_height.value or None,
            "promo_email": self.promo_email.value or None
        }
        self.view.updated_player = UpdatePlayerModel(**updated_player)
        await inter.response.send_message(f'Updates have been sent', delete_after=10)
        self.stop()

    async def on_error(self, inter: Interaction, error: Exception) -> None:
        await inter.response.send_message('Oops! Something went wrong.', ephemeral=True)
