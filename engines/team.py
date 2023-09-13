import discord

from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import TypeVar, Type
from beanie.operators import RegEx, Eq, LTE, GTE, ElemMatch
from bson import DBRef
from collections import namedtuple


B = TypeVar('B', bound=TeamBase)


class TeamMemberView(BaseModel):
    name: str

    class Settings:
        projection = {'_id': 0, 'name': '$member.name'}

class TeamNameView(BaseModel):
    name: str

class TeamEngine(BaseEngine):
    base = TeamBase

    def __init__(self):
        BaseEngine.te = self

    async def aggregate(self, match: str, target_collection: str, source_field: str):
        pipeline = [
            {'$lookup': {'from': target_collection, 'localField': f"{source_field}.$id", 'foreignField': "_id", 'as': 'member'}},
            {'$unwind': f"$member"}]
        return await TeamBase.find(TeamBase.name == match, with_children=True).aggregate(
            aggregation_pipeline=pipeline, projection_model=TeamMemberView).to_list()

    # I think ALL returns should be without links
    async def get_by(self, name: Optional[str] = None, member: Optional[PlayerBase] = None, game: Optional[GameBase] = None,
                region: Optional[Region] = None, active: Optional[bool] = None, aggregation: Optional[namedtuple] = None,
                registered_before: Optional[datetime] = None, registered_after: Optional[datetime] = None,
                output: Optional[SearchOutputType] = SearchOutputType.WithLinksToList) -> Optional[Union[list[B], B]]:
        base = TeamEngine.base
        search = base.find({}, with_children=True,
                           fetch_links=True if output in [SearchOutputType.WithLinksToList, SearchOutputType.WithLinksOnlyOne] else False)

        if name:
            search = search.find(RegEx(base.name, f'(?i){name}'))
        if member:
            search = search.find(ElemMatch(base.members, {'$in': [member]}))
        if game:
            game = DBRef('GameBase', game.id)
            search = search.find(ElemMatch(base.games, {'$in': [game]}))
        if region:
            search = search.find(Eq(base.region, Region))
        if active:
            search = search.find(Eq(base.active, True))
        if registered_before:
            search = search.find(LTE(base.registered_on, registered_before))
        if registered_after:
            search = search.find(GTE(base.registered_on, registered_after))

        match output:
            case SearchOutputType.WithLinksToList | SearchOutputType.NoLinksToList:
                return await search.to_list()
            case SearchOutputType.WithLinksOnlyOne | SearchOutputType.NoLinksOnlyOne:
                return await search.first_or_none()
            case SearchOutputType.OnlyNames:
                return await search.project(TeamNameView).to_list()
            case _:
                return await search.to_list()

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

