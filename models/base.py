import discord

from custom import VRPLBot, bot
from pydantic import BaseModel
from pymongo.collection import UpdateResult, InsertOneResult, DeleteResult
from typing import Optional, Iterable
from pydantic_mongo import AbstractRepository, ObjectIdField


class Base(BaseModel):
    _bot: VRPLBot = bot

    @property
    def bot(self) -> VRPLBot:
        """ this returns an instance of the discord client bot.
        This is useful when trying to get discord data from within the model. """
        return self._bot

    @classmethod
    def db(cls) -> AbstractRepository:
        """ returns the Repo for that specific model.
        Subclass this and return the type of Repo for the Model """
        raise NotImplemented

    def public_embed(self) -> discord.Embed:
        """ returns the public facing embed for the model """
        raise NotImplemented

    def private_embed(self) -> discord.Embed:
        """ returns the private facing embed for the model """
        raise NotImplemented

    def prep_save(self) -> 'Base':
        """ Subclass this to prep the Model before a save by updating its fields """
        return self

    def save(self) -> Optional['Base']:
        """ Save will save itself to the database, and return the saved object back """
        result = self.db().save(model=self.prep_save())
        if isinstance(result, InsertOneResult):
            if result.acknowledged:
                return self.get_by_id(result.inserted_id)
        if isinstance(result, UpdateResult):
            return self.get_by_id(self.id)
        return None

    def delete(self) -> DeleteResult:
        """ Deletes this model from the collection """
        return self.db().delete(model=self)

    @classmethod
    def get_by_id(cls, model_id: ObjectIdField) -> Optional['Base']:
        """ gets an id and returns the specific id """
        return cls.get_by_query({'id': model_id})

    @classmethod
    def get_by_discord(cls, item: discord.Member) -> Optional['Base']:
        """ gets a model by discord object """
        return cls.get_by_query({'discord_id': item.id})

    @classmethod
    def get_by_query(cls, query: dict) -> Optional['Base']:
        """ retrieves a Model by a key value pair """
        return cls.db().find_one_by(query=query)

    @classmethod
    def get_all(cls) -> Iterable['Base']:
        """ returns a list of all models in this collection """
        return list(cls.db().find_by(query={}, sort=[('id', -1)]))

    @classmethod
    def get_some(cls, search: str, key: str) -> Iterable['Base']:
        """ returns a list of all models matching the key and term """
        results = cls.get_all()
        return [result for result in results if search in result.dict().get(key)]
