from discord import Embed, Color
from config import DEFAULT_LOGO

from models.players import PlayerModel


class PlayerRegisterEmbed(Embed):
    def __init__(self):
        super().__init__(title="Player Registration", description="Click below to register a player")
        self.add_field(name='Registrations', value=f'By registering a player, you are agreeing to the VRPL code of '
                                                   f'conduct and rules')
        self.add_field(name='Game UID', value=f'You can find the game UID from the options menu. Please have it ready.')
        self.add_field(name='Calibrated Height', value=f'Please list the height you will be using in this league. '
                                                       f'You can update it later, but we track all edits to prevent '
                                                       f'abuse')
        self.add_field(name='Optionals', value=f'Providing your email is optional, and not required to participate')
        self.set_image(url='https://i.imgur.com/34eBdG2.png')
        self.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')


class PlayerEmbed(Embed):

    def __init__(self, player: PlayerModel):
        super().__init__(title=player.name, description=f'AKA {player.discord_user.name}')
        self.color = Color.orange()
        if player.discord_user.avatar:
            self.set_thumbnail(url=player.discord_user.avatar.url)
        else:
            self.set_thumbnail(url=DEFAULT_LOGO)
        self.set_footer(text=f'Banned: {player.is_banned} | Suspended: {player.is_suspended}')
        self.add_field(name='MMR', value=f'```{player.player_mmr}```')
        self.add_field(name='Game UID', value=f'```{player.game_uid}```')
        self.add_field(name='Calibrated Height', value=f'```{player.calibrated_height}```')


class SelfPlayerEmbed(PlayerEmbed):

    def __init__(self, player: PlayerModel):
        super().__init__(player=player)
        self.add_field(name='E-mail', value=f'```{player.promo_email}```')
        self.add_field(name='Warnings', value=f'```List Warnings Here```')
        self.add_field(name='Offences', value=f'```List Offences Here```')
