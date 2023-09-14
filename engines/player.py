import discord

import engines
from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import Type, TypeVar
from beanie.operators import RegEx, In, Eq, ElemMatch
from bson.dbref import DBRef

B = TypeVar('B', bound=PlayerBase)





class PlayerShortView(BaseModel):
    name: str


class PlayerEngine(BaseEngine):
    base = PlayerBase

    def __init__(self):
        BaseEngine.pe = self

    @property
    async def settings(self) -> Optional[PlayerSettings]:
        return await PlayerSettings.find_all().first_or_none()

    async def all_player_locations(self, location: Optional[str]=None) -> list[AllPlayerLocations]:
        return await AllPlayerLocations.find(Eq(AllPlayerLocations.location, location) if location else {}).to_list()

    async def update_settings(self, message: discord.Message, channel: discord.TextChannel) -> PlayerSettings:
        if not await self.settings:
            settings = PlayerSettings(channel_id=channel.id, message_id=message.id)
            return await settings.insert()
        else:
            return await self.settings.set({'channel_id': channel.id, 'message_id': message.id})

    async def get_by(self, name: Optional[str] = None, discord_member: Optional[int] = None, game: Optional[GameBase] = None,
                     location: Optional[str] = None, banned: Optional[bool] = None, suspended: Optional[bool] = None,
                     captain: Optional[bool] = None, co_captain: Optional[bool] = None, team: Optional[TeamBase] = None,
                     output: Optional[SearchOutputType] = SearchOutputType.WithLinksToList) -> Optional[list[B]]:
        if captain:
            base = CaptainPlayer
        elif co_captain:
            base = CoCaptainPlayer
        else:
            base = PlayerEngine.base

        search = base.find({}, with_children=True,
                           fetch_links=True if output in [SearchOutputType.WithLinksToList,
                                                          SearchOutputType.WithLinksOnlyOne] else False)

        if name:
            search = search.find(RegEx(base.name, f'(?i){name}'))
        if discord_member:
            search = search.find(Eq(base.discord_id, discord_member))
        if game:
            game = DBRef('GameBase', game.id)
            search = search.find(ElemMatch(base.games, {'$in': [game]}))
        if team:
            search = search.find(ElemMatch(base.teams, {'$in': [team]}))
        if location:
            search = search.find(Eq(base.location, location))
        if banned is not None:
            search = search.find(Eq(base.is_banned, banned))
        if suspended is not None:
            search = search.find(Eq(base.is_suspended, suspended))

        match output:
            case SearchOutputType.WithLinksToList | SearchOutputType.NoLinksToList:
                return await search.to_list()
            case SearchOutputType.WithLinksOnlyOne | SearchOutputType.NoLinksOnlyOne:
                return await search.first_or_none()
            case SearchOutputType.OnlyNames:
                return await search.project(PlayerShortView).to_list()
            case _:
                return await search.to_list()

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
