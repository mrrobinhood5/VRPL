from engines.shared import *
from engines.base import BaseEngine
from models import *
from pydantic import ValidationError
from typing import TypeVar, Type
from beanie.operators import RegEx, Eq, LTE, GTE, ElemMatch, In
from bson import DBRef
from collections import namedtuple

B = TypeVar('B', bound=TeamBase)
E = TypeVar('E', bound=BaseEngine)


class TeamNames(BaseModel):
    name: str


class TeamEngine(BaseEngine):
    base = TeamBase

    async def embed_maker(self, item: Optional[Any] = None, private: Optional[bool] = False) -> list[discord.Embed]:
        if not item: # this is for the dashboard
            embed = discord.Embed(title="Teams Dashboard", description="Options for managing League Teams")
            embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
        else:
            embed = discord.Embed(title=item.name, description=item.motto)
            embed.set_thumbnail(url=item.logo or 'https://i.imgur.com/VwQoXMB.png')
            embed.add_field(name='Region', value=item.region, inline=True)
            # Get Game
            item.game = await GameBase.get(item.game.ref.id, with_children=True)
            embed.add_field(name='Game', value=item.game.name, inline=True)
            # Get Members
            item.members = await PlayerBase.find(In('_id', [p.ref.id for p in item.members]), with_children=True).to_list()
            member_string = '\n'.join([f"`{member.name}{' - Captain`' if isinstance(member, CaptainPlayer) else ' - CoCaptain`' if isinstance(member, CoCaptainPlayer) else '`'}" for member in item.members])
            embed.add_field(name='Members', value=member_string, inline=True)
            embed.add_field(name='Tournaments', value='`Not Implemented`')
            embed.add_field(name='MMR', value='`Not Implemented`')
            embed.add_field(name='Rank', value='`Not Implemented`')
            embed.set_footer(text=f'Registered on VRPL on {item.registered_on}') # TODO: add last update time here

            if private:
                embed = embed
        return [embed]

    async def dashboard(self,
                        msg: Optional[discord.WebhookMessage] = None,
                        prev: Optional = None,
                        text: Optional[str] = None,
                        engine: Optional[E] = None) -> discord.ui.View:
        dashboard = await super().dashboard(msg=msg, prev=prev, text=text, engine=self)
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(FindButton(engine=self, search_function=self.get_by))
         .add_item(CreateButton())
         .add_item(UpdateButton())
         .add_item(DeleteButton()))
        return dashboard

    async def find_by_modal(self, inter, search_function: Callable, items: Optional = None) -> AsyncGenerator:
        items = [NameInput(), PlayerInput(), RegionInput(), GameInput()]
        results = await super().find_by_modal(inter, search_function, items)
        return results

    async def all_members_by_team(self, name: Optional[str] = None) -> Optional[list[AllTeamMembersByTeam]]:
        return await AllTeamMembersByTeam.find(
            Eq(AllTeamMembersByTeam.name, name) if name else {}).to_list()

    def get_by(self, *,
                     name: Optional[str] = None,
                     member: Optional[PlayerBase] = None,
                     game: Optional[GameBase] = None,
                     region: Optional[Region] = None,
                     active: Optional[bool] = None,
                     aggregation: Optional[namedtuple] = None,
                     registered_before: Optional[datetime] = None,
                     registered_after: Optional[datetime] = None,
                     output: Optional[SearchOutputType] = SearchOutputType.WithLinksToList) -> Optional[Union[list[B], B]]:

        search = self.base.find({}, with_children=True)

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

        return self.results_cursor(search)

    async def carousel(self, *,
                       msg=None,
                       prev: Optional[Awaitable] = None,
                       first: Optional[NamedTuple] = None,
                       generator: AsyncGenerator = None,
                       engine: Optional[E] = None) -> CarouselView:
        carousel = await super().carousel(msg=msg, prev=prev, first=first, generator=generator, engine=self)
        carousel.embeds = await self.embed_maker(first.item)
        (carousel.add_item(UpdateButton()).add_item(DeleteButton()))
        return carousel

    # NOTHING BELOW IS IMPLEMENTED
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

