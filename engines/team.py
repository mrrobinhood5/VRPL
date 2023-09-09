from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import TypeVar, Type

base = TeamBase
B = TypeVar('B', bound=TeamBase)

class TeamEngine(BaseEngine):

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

