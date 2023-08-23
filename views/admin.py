import discord

from views import PersistentDashboardBase, DashboardEmbedBase


class AdminDashboardEmbed(DashboardEmbedBase):

    def __init__(self):
        title = "Administrator Dashboard"
        description = ("Use this dashboard to access other administrator functions. "
                       "Only Staff will be able to interact with this.")
        color = discord.Color.red()
        super().__init__(title=title, description=description, color=color)




class AdminDashboard(PersistentDashboardBase):

    def __init__(self):
        super().__init__()


    def embed(self):
        embed = AdminDashboardEmbed()
        embed.add_field(name="Players", value="Create, Edit and Delete player profiles on behalf of players") \
        .add_field(name="Teams", value="Create, Edit, and Delete team profiles on behalf of a team") \
        .add_field(name="Tournaments", value="Create, and and delete Maps, Tournaments, Weeks, Matches and Scores.")\
        .set_thumbnail()