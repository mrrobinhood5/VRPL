import discord
from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import Type, TypeVar
from beanie.operators import RegEx, In, Eq

base = PlayerBase
B = TypeVar('B', bound=PlayerBase)

class PlayerEngine(BaseEngine):

    def __init__(self):
        BaseEngine.pe = self

    @property
    async def settings(self) -> Optional[PlayerSettings]:
        return await PlayerSettings.find_all().first_or_none()

    async def update_settings(self, message: discord.Message, channel: discord.TextChannel) -> PlayerSettings:
        if not await self.settings:
            settings = PlayerSettings(channel_id=channel.id, message_id=message.id)
            return await settings.insert()
        else:
            return await self.settings.set({'channel_id': channel.id, 'message_id': message.id})

    async def get_by_name(self, name: str) -> Optional[B]:
        return await base.find(RegEx(base.name, f'(?i){name}'), with_children=True, fetch_links=True).first_or_none()

    async def get_by_discord(self, discord_id: int) -> Optional[B]:
        return await base.find(Eq(base.discord_id, discord_id), with_children=True, fetch_links=True).first_or_none()

    async def get_by_location(self, location: Location) -> Optional[list[B]]:
        return await base.find(Eq(base.location, location), with_children=True, fetch_links=True).to_list()

    async def get_by_alias(self, name: str) -> Optional[list[B]]:
        return await base.find(In(name, base.alias), with_children=True, fetch_links=True).to_list()

    async def get_banned(self) -> Optional[list[B]]:
        return await base.find(Eq(base.is_banned, True), with_children=True, fetch_links=True).to_list()

    async def get_suspended(self) -> Optional[list[B]]:
        return await base.find(Eq(base.is_suspended, True), with_children=True, fetch_links=True).to_list()

    async def get_captains(self) -> Optional[list[CaptainPlayer]]:
        return await CaptainPlayer.find({}, fetch_links=True).to_list()

    async def get_co_captains(self) -> Optional[list[CoCaptainPlayer]]:
        return await CoCaptainPlayer.find({}, fetch_links=True).to_list()

    async def register_player(self, **kwargs) -> NormalPlayer:
        try:
            return await NormalPlayer(**kwargs).insert()
        except ValidationError as e:
            raise e

    async def make_captain(self, player: NormalPlayer) -> CaptainPlayer:
        """ This should only be called by the Team Engine, or Admin Engine  """
        try:
            captain = CaptainPlayer(**player.dict())
            (await player.delete(), await captain.insert())
            return captain
        except ValidationError as e:
            raise e

    async def make_co_captain(self, player: Type[NormalPlayer]) -> CoCaptainPlayer:
        try:
            co_captain = CoCaptainPlayer(**dict(player), check_fields=False)
            (await player.delete(), await co_captain.insert())
            return co_captain
        except ValidationError as e:
            raise e

    # async def update(self, base: Type[B], updates: dict) -> Type[B]:
    #     try:
    #         return await base.set(updates)
    #     except ValidationError as e:
    #         raise e
