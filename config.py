import os
from discord import Intents


BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_PREFIX = "."
INTENTS = Intents(
    guilds=True, members=True, messages=True, reactions=True,
    bans=False, emojis=False, integrations=False, webhooks=True, invites=False, voice_states=False, presences=False,
    typing=False, message_content=True)
BOT_OWNER = os.getenv('BOT_OWNER')
DEFAULT_LOGO = "https://i.imgur.com/d4SLqgD.png"
QUOTES_URL = "https://zenquotes.io/api/random"

cogs = os.listdir('./cogs')
cogs.remove("__pycache__") if "__pycache__" in cogs else 0
