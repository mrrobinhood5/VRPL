from discord.ui import Select, View
from discord import SelectOption, Interaction


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
