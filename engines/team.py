from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import TypeVar, Type
from beanie.operators import RegEx, Eq, LTE, GTE

base = TeamBase
B = TypeVar('B', bound=TeamBase)


class TeamEngine(BaseEngine):

    def __init__(self):
        BaseEngine.te = self

    async def get_by_name(self, name: str) -> Optional[B]:
        return await base.find(RegEx(base.name, f'(?i){name}'), with_children=True, fetch_links=True).first_or_none()

    async def get_by_region(self, region: Region) -> Optional[list[B]]:
        return await base.find(Eq(base.region, region), with_children=True, fetch_links=True).to_list()

    async def get_active(self) -> Optional[list[B]]:
        return await base.find(Eq(base.active, True), with_children=True, fetch_links=True).to_list()

    async def registered_before(self, date: datetime) -> Optional[list[B]]:
        return await base.find(LTE(base.registered_on, date), with_children=True, fetch_links=True).to_list()

    async def registered_after(self, date: datetime) -> Optional[list[B]]:
        return await base.find(GTE(base.registered_on, date), with_children=True, fetch_links=True).to_list()


    async def register_team(self, base: Optional[Type[B]] = StandardTeam, **kwargs) -> Type[B]:
        try:
            return await base(**kwargs).insert()
        except ValidationError as e:
            raise e

    async def add_player(self, team: Type[B], player: Type[B]) -> Type[B]:
        if team.full:
            raise ValueError('Team is Full')
        team.members.append(player)
        await team.save()
        return team

