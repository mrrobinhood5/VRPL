import asyncio
from datetime import datetime
from pprint import pprint as print
from utils import all_models
from database import Database
from discord import Embed

from beanie import init_beanie, WriteRules
from models import *


async def example():
    db = Database().db
    models = all_models()
    await init_beanie(database=db, document_models=models)


    # vurple = VRPLObject()
    # player = PlayerBase(discord_id=123, name="Robinhood6", game_uid='abc123', height=4.0, location=Location.US, registered_date=datetime.now())
    #
    # await vurple.insert()
    # await player.insert()
    #
    # me = NormalPlayer(discord_id=456, name="asdfsf", game_uid='abc123', height=4.0, location=Location.US, registered_date=datetime.now())
    # captain = CaptainPlayer(discord_id=456, name="capitain hook", game_uid='abc123', height=4.0, location=Location.US, registered_date=datetime.now())

    # await captain.insert()
    # await me.insert()

    # Fetch models

    players = await PlayerBase.find_all(fetch_links=True, with_children=True).to_list()
    print(players)

#     import json
#     temp_embed_json = """{
#   "author": {
#     "name": "Info",
#     "url": "https://example.com"
#   },
#   "title": "Example Title",
#   "url": "https://example.com",
#   "description": "This is an example description. Markdown works too!
#
# https://automatic.links
# > Block Quotes
# ```
# Code Blocks
# ```
# *Emphasis* or _emphasis_
# `Inline code` or ``inline code``
# [Links](https://example.com)
# <@123>, <@!123>, <#123>, <@&123>, @here, @everyone mentions
# ||Spoilers||
# ~~Strikethrough~~
# **Strong**
# __Underline__",
#   "fields": [
#     {
#       "name": "Field Name",
#       "value": "This is the field value."
#     },
#     {
#       "name": "The first inline field.",
#       "value": "This field is inline.",
#       "inline": true
#     },
#     {
#       "name": "The second inline field.",
#       "value": "Inline fields are stacked next to each other.",
#       "inline": true
#     },
#     {
#       "name": "The third inline field.",
#       "value": "You can have up to 3 inline fields in a row.",
#       "inline": true
#     },
#     {
#       "name": "Even if the next field is inline...",
#       "value": "It won't stack with the previous inline fields.",
#       "inline": true
#     }
#   ],
#   "image": {
#     "url": "https://cubedhuang.com/images/alex-knight-unsplash.webp"
#   },
#   "thumbnail": {
#     "url": "https://dan.onl/images/emptysong.jpg"
#   },
#   "color": "#00b0f4",
#   "footer": {
#     "text": "Example Footer",
#     "icon_url": "https://slate.dan.onl/slate.png"
#   },
#   "timestamp": 1692813061033
# }"""
#     e = json.loads(temp_embed_json, strict=False)
#
#     VRPLEmbed = EmbedBase.model_validate(e)
#     print(VRPLEmbed)
#     await VRPLEmbed.insert()

    embeds = EmbedBase.find_all()
    async for e in embeds:
        print(Embed.from_dict(e.dict()).to_dict())



    # print(author)


if __name__ == "__main__":
    asyncio.run(example())
