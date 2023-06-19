import discord
import requests

from discord import app_commands
from discord.ext import commands


class MiscCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='hello')
    async def hello(self, inter: discord.Interaction):
        """ Just says Hello and gives inspirational quote """
        quote = requests.get('https://zenquotes.io/api/random').json()[0]
        embed = discord.Embed(color=discord.Color.brand_green(), title=f'{quote.get("a")}:',
                              description=f'{quote.get("q")}')
        await inter.response.send_message(f'### Well hello to you too {inter.user.name}\n', embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MiscCog(bot))
