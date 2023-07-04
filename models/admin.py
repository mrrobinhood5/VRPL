import discord
from pymongo.results import UpdateResult, InsertOneResult

from models.base import Base
from typing import Optional, Union
from pydantic import validator, Field
from bson import ObjectId
from pydantic_mongo import ObjectIdField, AbstractRepository
from database import DBConnect


class SettingsModel(Base):
    id: ObjectIdField = None

    teams_channel_id: Optional[int]
    teams_message_id: Optional[int]

    players_channel_id: Optional[int]
    players_message_id: Optional[int]

    teams_channel: Optional[discord.TextChannel] = Field(default=None, exclude=True)
    players_channel: Optional[discord.TextChannel] = Field(default=None, exclude=True)

    teams_message: Optional[discord.Message] = Field(default=None, exclude=True)
    players_message: Optional[discord.Message] = Field(default=None, exclude=True)

    @validator('teams_channel_id', 'players_channel_id')
    def check_channel_id(cls, v):
        """ validates the ids are valid """
        if channel := cls._bot.get_channel(v):
            return v
        else:
            raise ValueError("Not a valid Channel ID")

    @validator('teams_channel', always=True)
    def get_teams_channel(cls, v, values):
        if values.get('teams_channel_id', None):
            return cls._bot.get_channel(v)
        else:
            return None

    @validator('players_channel', always=True)
    def get_players_channel(cls, v, values):
        if values.get('players_channel_id', None):
            return cls._bot.get_channel(v)
        else:
            return None

    def save(self) -> Union[UpdateResult, InsertOneResult]:
        _ = self.dict(exclude={'teams_channel', 'players_channel', 'teams_message', 'players_message'})
        self.db().save(model=_)

    async def get_messages(self):
        """ asyncly gets the messages. Cannot be done during validation, has to be called explicitly """
        if msg := self.teams_message_id:
            self.teams_message = await self.teams_channel.fetch_message(msg)
        if msg := self.players_message_id:
            self.players_message = await self.players_channel.fetch_message(msg)

    @classmethod
    def db(cls):
        """ Returns a connection to a collection for this model """
        return SettingsRepo(DBConnect().db)

    @classmethod
    def get(cls) -> 'SettingsModel':
        """ retrieves the settings from db if any """
        result = cls.db().find_one_by(query={})
        return result or SettingsModel()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SettingsRepo(AbstractRepository[SettingsModel]):
    class Meta:
        collection_name = 'settings'
