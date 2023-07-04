import discord

from custom import VRPLBot, bot
from pydantic import BaseModel
from pymongo.collection import UpdateResult, InsertOneResult, DeleteResult
from typing import Union



class Base(BaseModel):
    _bot: VRPLBot = bot

    @property
    def bot(self):
        return self._bot

    @classmethod
    def db(cls):
        raise NotImplemented

    def public_embed(self) -> discord.Embed:
        raise NotImplemented

    def private_embed(self) -> discord.Embed:
        raise NotImplemented

    def save(self) -> Union[UpdateResult, InsertOneResult]:
        """ Saves this model to the collection """
        return self.db().save(model=self)

    def delete(self) -> DeleteResult:
        """ Deletes this model from the collection """
        return self.db().delete(model=self)

