import random

from base_classes import Player, Tournament, Game, Season
from errors import TournamentError
from testing_utils.test_data import c_tournaments, seasons, games
from utils import generate_guid, generate_username
from transactions.transaction_log import TransactionType, TransactionLogger
from database import db
from db_interface import DbInterface
from time import sleep
from utils import generate_players
from rich import inspect
# Transaction log testing uses DB, so it needs to be in an event loop


async def main():
    # For testing purposes, clear the logger collection every time
    await db.logger.drop()

    # logger instance will handle what gets logged and provide a doc to insert
    logger = TransactionLogger()

    # generate test players
    generate_players(500)

    for season in seasons:
        Season(**season)

    for game in games:
        Game(**game)

    # generate tournaments
    for tournament in c_tournaments:
        try:
            Tournament(**tournament,
                       belongs_to_game=Game.get('con').id,
                       belongs_to_season=Season.get('2').id)
        except TournamentError as e:
            pass
    # inspect(Player.instances()[5].to_dict())


    if logger.queue:
        await db['logger'].insert_many(x for x in logger.process_queue())
    print(logger.queue)

    # if Player.instances():
        # this is where im trying to update any instances that have changed
        # await db['players'].update_one({}, )

    # Join some 1v1 tournaments
    for player in Player.instances():
        if random.randint(0, 1):
            player.join_tournament(Tournament.get('1v1'))

    if logger.queue:
        await db['logger'].insert_many(x for x in logger.process_queue())
    print(logger.queue)

    # time delay before processing more
    sleep(60)


# start the event loop
loop = db.get_io_loop()
loop.run_until_complete(main())
