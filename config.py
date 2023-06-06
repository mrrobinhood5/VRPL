import os
from discord import Intents

# discord CONSTANTS
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_PREFIX = "."
INTENTS = Intents(
    guilds=True, members=True, messages=True, reactions=True,
    bans=False, emojis=False, integrations=False, webhooks=True, invites=False, voice_states=False, presences=False,
    typing=False, message_content=True)
BOT_OWNER = os.getenv('BOT_OWNER')
DEFAULT_LOGO = "https://i.imgur.com/d4SLqgD.png"

# server SPECIFIC
# TODO: move these to the database and make admin commands to set them
PLAYER_UPDATE_CHANNEL = 1115090885672194120
TEAM_UPDATE_CHANNEL = 1115090917234323476

# daily quote
QUOTES_URL = "https://zenquotes.io/api/random"

cogs = os.listdir('./cogs')
cogs.remove("__pycache__") if "__pycache__" in cogs else 0
