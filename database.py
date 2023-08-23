from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from os import getenv


class Database:
    """ Database Object, initializes for AsyncMotor"""
    def __init__(self):
        self.db_user = getenv('DB_USER')
        self.db_pw = getenv('DB_PW')
        self.db_name = getenv('DB_NAME')
        self.db_url = getenv('DB_URL')

    @property
    def client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(f"mongodb+srv://{self.db_user}:{self.db_pw}@{self.db_url}")
        # return MongoClient(f"mongodb+srv://{self.db_user}:{self.db_pw}@{self.db_url}")

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self.client[self.db_name]
