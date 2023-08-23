import asyncio
from datetime import datetime
from pprint import pprint as print
from utils import all_models
from database import Database

from beanie import init_beanie
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


if __name__ == "__main__":
    asyncio.run(example())
