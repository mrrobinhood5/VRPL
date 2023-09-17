import discord

from discord import Interaction
from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import TypeVar, Type
from beanie.operators import RegEx, Eq, LTE, GTE, ElemMatch
from bson import DBRef
from collections import namedtuple


B = TypeVar('B', bound=TeamBase)


class TeamNames(BaseModel):
    name: str


class TeamEngine(BaseEngine):
    base = TeamBase

    class DashboardView(BaseEngine.DashboardView):

        def __init__(self, msg: Optional[discord.WebhookMessage] = None, prev: Optional = None):
            super().__init__(msg, prev)
            self._embed = (discord.Embed(colour=discord.Colour.dark_blue(),
                                         title='Team Dash',
                                         description='Team Options')
                           .set_thumbnail(url='https://i.imgur.com/VwQoXMB.png'))

        @discord.ui.button(custom_id='team_view.find', style=discord.ButtonStyle.secondary, label='Find By')
        async def find(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Team Find', embed=None, view=None)
            self.stop()
            self.next = inter.client.find_by()
            self.prev = inter.client.te.dashboard(prev=self.prev)
            await self.msg.delete()

        @discord.ui.button(custom_id='team_view.create', style=discord.ButtonStyle.green, label='Create')
        async def create(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Team Create', embed=None, view=None)
            self.stop()
            self.next = inter.client.te.create()
            self.prev = inter.client.te.dashboard(prev=self.prev)

        @discord.ui.button(custom_id='team_view.update', style=discord.ButtonStyle.green, label='Update')
        async def update(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Player Update', embed=None, view=None)
            self.stop()
            self.next = inter.client.te.update()
            self.prev = inter.client.te.dashboard(prev=self.prev)

        @discord.ui.button(custom_id='team_view.delete', style=discord.ButtonStyle.green, label='Delete')
        async def delete(self, inter: Interaction, button: discord.ui.Button):
            await self.msg.edit(content='Accessing Team Delete', embed=None, view=None)
            self.stop()
            self.next = inter.client.te.delete()
            self.prev = inter.client.te.dashboard(prev=self.prev)

    async def all_members_by_team(self, name: Optional[str] = None) -> Optional[list[AllTeamMembersByTeam]]:
        return await AllTeamMembersByTeam.find(
            Eq(AllTeamMembersByTeam.name, name) if name else {}).to_list()

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
                return await search.project(TeamNames).to_list()
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

