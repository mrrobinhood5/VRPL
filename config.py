from os import getenv, listdir
from discord import Intents

# OS ENV
BOT_TOKEN = getenv('BOT_TOKEN')
TESTING_GUILD = getenv('TESTING_GUILD')
BOT_PREFIX = "."
BOT_OWNER = getenv('BOT_OWNER')

# DISCORD ENV
INTENTS = Intents(
    guilds=True, members=True, messages=True, reactions=True,
    bans=False, emojis=False, integrations=False, webhooks=True, invites=False, voice_states=False, presences=False,
    typing=False, message_content=True)

DEFAULT_TEAM_LOGO = "https://cdn.discordapp.com/emojis/1058108114626416721.webp?size=96&quality=lossless"
DEFAULT_PLAYER_LOGO = "https://i.imgur.com/d4SLqgD.png"
QUOTES_URL = "https://zenquotes.io/api/random"

# COGS
COGS = listdir('./cogs')
COGS.remove("__pycache__") if "__pycache__" in COGS else 0
