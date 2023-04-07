from base_classes import *
from testing_utils import test_data
from testing_utils.utils import *

logger = TransactionLogger()

players = 30

Season(logger=logger, **test_data.seasons[1])
Game(logger=logger, **test_data.games[0])

Tournament(logger=logger,
           belongs_to_game=Game.instances()[0].id,
           belongs_to_season=Season.instances()[0].id,
           **test_data.c_tournaments[1])

for x in range(0, players):
    Player(logger=logger,
           game_uid=generate_guid(),
           name=generate_username(),
           height=str(randint(52, 72)))

for player in Player.instances():
    player.join_tournament(Tournament.get('1v1')[0])


