from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis_interface import RedisClient
from os import getenv

db_user = getenv('DB_USER')
db_pw = getenv('DB_PW')

client = AsyncIOMotorClient(f"mongodb+srv://{db_user}:{db_pw}@cluster0.i31qn.mongodb.net/?retryWrites=true&w=majority")
db: AsyncIOMotorDatabase = client['VRCL']

config_db = RedisClient(db=0)
seasons_db = RedisClient(db=1)
games_db = RedisClient(db=2)
tournaments_db = RedisClient(db=3)
teams_db = RedisClient(db=4)
players_db = RedisClient(db=5)


