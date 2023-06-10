from discord import Embed


class TeamRegisterEmbed(Embed):
    def __init__(self):
        super().__init__(title="Team Registration", description="Click below to register a team")
        self.add_field(name='Registrations',
                       value=f'By registering a team, you are opening up sign-ups for your team. Only a Captain / '
                             f'Co-Captain can approved the team join requests')
        self.add_field(name='Team Name', value=f'You will be submitting the proper name for your team')
        self.add_field(name='Team Motto', value=f'This will be the text used to describe your team. ')
        self.add_field(name='Team Logo', value=f'You can use an imgur link or a discord link to provide the team URL')
        self.set_image(url='https://i.imgur.com/34eBdG2.png')
        self.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
