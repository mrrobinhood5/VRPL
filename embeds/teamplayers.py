from discord import Embed, Color
from models.teamplayers import FullTeamModel
from models.teams import TeamModel
from config import DEFAULT_LOGO
from typing import Union


class FullTeamEmbed(Embed):

    def __init__(self, team: FullTeamModel):
        super().__init__(title=team.name, description=team.team_motto)
        self.color = Color.blurple()
        self.set_thumbnail(url=team.team_logo or DEFAULT_LOGO)
        self.set_footer(text=f'Active: {team.active}')
        self.add_field(name='MMR', value=f'```{team.team_mmr}```', inline=True)
        self.add_field(name='Captain', value=f'```{team.captain.name}```')
        self.add_field(name='CoCaptain', value=f'```{team.co_captain.name if team.co_captain else None}```')
        players = f''
        for player in team.members:
            players += f'`{player.name}`\n'
        self.add_field(name='Players', value=players)


class OwnTeamEmbed(FullTeamEmbed):

    def __init__(self, team: FullTeamModel):
        super().__init__(team=team)
        self.add_field(name='Warnings', value=f'```Warnings Here```')
        self.add_field(name='Infractions', value=f'```Infractions Here```')


class NewTeamEmbed(Embed):  # TODO: make this accept both a FullTeamModel or TeamModel

    def __init__(self, team: Union[FullTeamModel, TeamModel]):
        super().__init__(title=team.name, description=team.team_motto)
        self.color = Color.blurple()
        self.set_thumbnail(
            url=team.team_logo or "https://cdn.discordapp.com/emojis/1058108114626416721.webp?size=96&quality=lossless")
        self.set_footer(text=f'Active: {team.active}')
        self.add_field(name='MMR', value=f'```{team.team_mmr}```', inline=True)
        self.add_field(name='Captain', value=f'```{team.captain.name}```')



