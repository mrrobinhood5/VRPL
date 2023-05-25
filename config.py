import os
from discord import Intents

# discord CONSTANTS
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_PREFIX = "."
INTENTS = Intents(
    guilds=True, members=True, messages=True, reactions=True,
    bans=False, emojis=False, integrations=False, webhooks=True, invites=False, voice_states=False, presences=False,
    typing=False, message_content=True)
