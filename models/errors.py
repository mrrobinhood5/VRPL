import discord
from fastapi.exceptions import HTTPException


class GenericErrorEmbed(discord.Embed):

    def __init__(self, player: discord.User, error: HTTPException):
        super().__init__(title=f'{error.status_code} Error', description=f'```{error.detail}```')
        self.set_thumbnail(url=player.avatar.url)
        self.color = discord.Color.brand_red()
        self.set_footer(icon_url="https://cdn.discordapp.com/emojis/1033805413138845736.webp?size=96&quality=lossless",
                        text="Error Message")
