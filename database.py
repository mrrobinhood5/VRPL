from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from pymongo import MongoClient
from pymongo.database import Database

# from pymongo.database import Database, MongoClient
from os import getenv


class DBConnect:
    """ This DB Connect needs to get passed into each AbstractRepo subclass """
    def __init__(self):
        self.db_user = getenv('DB_USER')
        self.db_pw = getenv('DB_PW')
        self.db_name = getenv('DB_NAME')
        self.db_url = getenv('DB_URL')

    @property
    def client(self) -> MongoClient:
        # return AsyncIOMotorClient(f"mongodb+srv://{self.db_user}:{self.db_pw}@{self.db_url}")
        return MongoClient(f"mongodb+srv://{self.db_user}:{self.db_pw}@{self.db_url}")

    @property
    def db(self) -> Database:
        return self.client[self.db_name]


# async def db_get_settings() -> Optional[dict]:
#     settings = await db['settings'].find_one({}, sort=[('_id', DESCENDING)])
#     return settings
#
#
# async def db_set_settings(obj: dict) -> Optional[dict]:
#     obj = jsonable_encoder(obj)
#     result = await db['settings'].update_one({"_id": obj.get('_id')}, {"$set": obj})
#     return result
#
#
# async def db_add_one(name: str, obj: Union[PlayerModel, TeamModel, PlayerTeamModel, SettingsModel]) -> Optional[dict]:
#     obj = jsonable_encoder(obj)
#     new_obj = await db[name].insert_one(obj)
#     created_obj = await db[name].find_one({"_id": new_obj.inserted_id})
#     return created_obj
#
#
# async def db_find_all(name: str, amt: int) -> list[Optional[dict]]:
#     results = await db[name].find().to_list(amt)
#     return results
#
#
# async def db_find_some(name: str, db_filter: dict,
#                        exclude: Union[dict, None] = None, amt: int = 100) -> list[Optional[dict]]:
#     results = await db[name].find(db_filter, projection=exclude).to_list(amt)
#     return results
#
#
# async def db_find_one(name: str, obj_id: str, projection: dict = None) -> Optional[dict]:
#     result = await db[name].find_one({"_id": obj_id}, projection=projection)
#     return result
#
#
# async def db_find_one_by_other(name: str, query: dict) -> Optional[dict]:
#     result = await db[name].find_one(query)
#     return result
#
#
# async def db_update_one(name: str, obj_id: str, obj: dict) -> Optional[dict]:
#     obj = jsonable_encoder(obj)
#     result = await db[name].update_one({"_id": obj_id}, {"$set": obj})
#     return result
#
#
# async def db_update_one_discord(name: str, obj_id: int, obj: dict) -> Optional[dict]:
#     obj = jsonable_encoder(obj)
#     result = await db[name].update_one({'discord_id': obj_id}, {'$set': obj})
#     return result
#
#
# async def db_count_items(name: str, query: Optional[dict] = None) -> Optional[dict]:
#     result = await db[name].count_documents(query)
#     return result
#
#
# async def db_delete_one(name: str, obj_id: str) -> Optional[dict]:
#     result = await db[name].delete_one({'_id': obj_id})
#     return result
#
#
# async def db_delete_one_by_other(name: str, query: dict) -> Optional[dict]:
#     result = await db[name].delete_one(query)
#     return result
