import discord

from custom import VRPLBot, bot
from pydantic import BaseModel


class Base(BaseModel):
    _bot: VRPLBot = bot

    @property
    def bot(self) -> VRPLBot:
        """ this returns an instance of the discord client bot.
        This is useful when trying to get discord data from within the model. """
        return self._bot

    def public_embed(self) -> discord.Embed:
        """ returns the public facing embed for the model """
        raise NotImplemented

    def private_embed(self) -> discord.Embed:
        """ returns the private facing embed for the model """
        raise NotImplemented

