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
