from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import Type, TypeVar
from beanie.operators import RegEx

base = PlayerBase
B = TypeVar('B', bound=PlayerBase)


class PlayerEngine(BaseEngine):

    async def get_by_discord(self, discord_id: int) -> Optional[B]:
        return await base.find({'discord_id': discord_id}, with_children=True, fetch_links=True).first_or_none()

    async def get_by_name(self, name: str) -> Optional[B]:
        return await base.find(RegEx(base.name, name), with_children=True, fetch_links=True).first_or_none()

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
