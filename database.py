from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi.encoders import jsonable_encoder
from typing import Union
from classes.players import PlayerModel, PlayerTeamModel
from classes.teams import TeamModel
from os import getenv

db_user = getenv('DB_USER')
db_pw = getenv('DB_PW')

client = AsyncIOMotorClient(f"mongodb+srv://{db_user}:{db_pw}@cluster0.i31qn.mongodb.net/?retryWrites=true&w=majority")
db: AsyncIOMotorDatabase = client['VRPL']


async def db_add_one(obj: Union[PlayerModel, TeamModel, PlayerTeamModel], db_name: str):
    obj = jsonable_encoder(obj)
    new_obj = await db[db_name].insert_one(obj)
    created_obj = await db[db_name].find_one({"_id": new_obj.inserted_id})
    return created_obj


async def db_find_all(db_name: str, amt: int):
    results = await db[db_name].find().to_list(amt)
    return results


async def db_find_some(db_name: str, db_filter: dict, exclude: Union[dict, None] = dict):
    results = await db[db_name].find(db_filter).to_list(100)
    return results


async def db_find_one(obj_id: str, db_name: str):
    result = await db[db_name].find_one({"_id": obj_id})
    return result


async def db_update_one(obj_id: str, db_name: str, obj: dict):
    result = await db[db_name].update_one({"_id": obj_id}, {"$set": obj})
    return result
