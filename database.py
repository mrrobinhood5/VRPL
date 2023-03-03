from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis_interface import RedisClient

client = AsyncIOMotorClient("mongodb+srv://vrcl_user:DiMvMPCVGF7zXdB@cluster0.i31qn.mongodb.net/?retryWrites=true&w=majority")
db: AsyncIOMotorDatabase = client['VRCL']

config_db = RedisClient(db=0)
seasons_db = RedisClient(db=1)
games_db = RedisClient(db=2)
tournaments_db = RedisClient(db=3)
teams_db = RedisClient(db=4)
players_db = RedisClient(db=5)


