from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import DESCENDING
from fastapi.encoders import jsonable_encoder
from typing import Union
from models.players import PlayerModel, PlayerTeamModel
from models.settings import SettingsModel
from models.teams import TeamModel
from os import getenv

db_user = getenv('DB_USER')
db_pw = getenv('DB_PW')
db_name = getenv('DB_NAME')

client = AsyncIOMotorClient(f"mongodb+srv://{db_user}:{db_pw}@cluster0.i31qn.mongodb.net/?retryWrites=true&w=majority")
db: AsyncIOMotorDatabase = client[db_name]


async def db_get_settings() -> dict:
    settings = await db['settings'].find_one({}, sort=[('_id', DESCENDING)])
    return settings


async def db_set_settings(obj: dict):
    result = await db['settings'].insert_one(obj)
    return result


async def db_add_one(db_name: str, obj: Union[PlayerModel, TeamModel, PlayerTeamModel, SettingsModel]):
    obj = jsonable_encoder(obj)
    new_obj = await db[db_name].insert_one(obj)
    created_obj = await db[db_name].find_one({"_id": new_obj.inserted_id})
    return created_obj


async def db_find_all(db_name: str, amt: int) -> list[dict]:
    results = await db[db_name].find().to_list(amt)
    return results


async def db_find_some(db_name: str, db_filter: dict, exclude: Union[dict, None] = None, amt: int = 100):
    results = await db[db_name].find(db_filter, projection=exclude).to_list(amt)
    return results


async def db_find_one(db_name: str, obj_id: str, projection: dict = None) -> dict:
    result = await db[db_name].find_one({"_id": obj_id}, projection=projection)
    return result


async def db_find_one_by_other(db_name: str, query: dict) -> Union[dict, None]:
    result = await db[db_name].find_one(query)
    return result


async def db_update_one(db_name: str, obj_id: str, obj: dict):
    obj = jsonable_encoder(obj)
    result = await db[db_name].update_one({"_id": obj_id}, {"$set": obj})
    return result


async def db_update_one_discord(db_name: str, obj_id: str, obj: dict):
    obj = jsonable_encoder(obj)
    result = await db[db_name].update_one({'discord_id': obj_id}, {'$set': obj})
    return result


async def db_count_items(db_name: str, query: Union[dict, None] = None):
    result = await db[db_name].count_documents(query)
    return result


async def db_delete_one(db_name: str, obj_id: str):
    result = await db[db_name].delete_one({'_id': obj_id})
    return result
