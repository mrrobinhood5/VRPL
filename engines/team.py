import beanie

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

    @BaseEngine.embed_maker
    async def embed_maker(self,
                          embeds: Embeds,
                          item: Type[B] = None,
                          private: Optional[bool] = False) -> list[discord.Embed]:
        if not item: # this is for the dashboard
            embed = embeds.public
            embed.title="Teams Dashboard"
            embed.description="Options for managing League Teams"
        else:
            embed = embeds.public
            embed.title = item.name
            embed.description = f'`{item.motto}`'
            embed.set_thumbnail(url=item.logo) if item.logo else 0
            embed.add_field(name='Region', value=f'`{item.region.value}`', inline=True)
            # Get Game
            if isinstance(item.game, beanie.Link):
                item.game = await GameBase.get(item.game.ref.id, with_children=True)
            embed.add_field(name='Game', value=f'`{item.game.name}`', inline=True)
            # Get Members
            if isinstance(item.members[0], beanie.Link):
                item.members = await PlayerBase.find(In('_id', [p.ref.id for p in item.members]), with_children=True).to_list()
            member_string = '\n'.join([f"`{member.name}{' - Captain`' if isinstance(member, CaptainPlayer) else ' - CoCaptain`' if isinstance(member, CoCaptainPlayer) else '`'}" for member in item.members])
            embed.add_field(name='Members', value=member_string, inline=True)
            embed.add_field(name='Tournaments', value='`Not Implemented`')
            embed.add_field(name='MMR', value='`Not Implemented`')
            embed.add_field(name='Rank', value='`Not Implemented`')
            embed.set_footer(text=f'Registered on VRPL on {item.registered_on}') # TODO: add last update time here

            if private:
                pembed = embeds.private
                return [embed, pembed]
        return [embed]

    @BaseEngine.dashboard
    async def dashboard(self, /, dashboard: discord.ui.View, *args, **kwargs) -> discord.ui.View:
        dashboard.embeds = await self.embed_maker()
        (dashboard.add_item(FindButton(engine=self, search_function=self.get_by))
         .add_item(CreateButton(engine=self, search_function=self.get_by))
         .add_item(UpdateButton())
         .add_item(DeleteButton()))
        return dashboard

    @BaseEngine.find_by_modal
    async def find_by_modal(self, /, modal: discord.ui.Modal) -> discord.ui.Modal:
        items = [StandardInput(label='name', placeholder='Leave blank for ALL'),
                 StandardInput(label='player', placeholder='Leave blank for ALL'),
                 StandardInput(label='region', placeholder='Leave blank for ALL'),
                 StandardInput(label='game', placeholder='Leave blank for ALL')]
        [modal.add_item(x) for x in items]
        return modal

    @BaseEngine.carousel
    async def carousel(self, /,
                       carousel: CarouselView) -> CarouselView:
        (carousel.add_item(UpdateButton())
                 .add_item(DeleteButton()))
        return carousel

    # SEARCH methods
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
                     registered_after: Optional[datetime] = None) -> Result:
        search = self.base.find({}, with_children=True)
        pipeline = []
        if name:
            search = search.find(RegEx(self.base.name, f'(?i){name}'))
        if member:
            search = search.find(ElemMatch(self.base.members, {'$in': [member]}))
        if game:
            game = DBRef('GameBase', game.id)
            search = search.find(ElemMatch(self.base.games, {'$in': [game]}))
        if region:
            search = search.find(Eq(self.base.region, Region))
        if active:
            search = search.find(Eq(self.base.active, True))
        if registered_before:
            search = search.find(LTE(self.base.registered_on, registered_before))
        if registered_after:
            search = search.find(GTE(self.base.registered_on, registered_after))

        return self.results_cursor(search.aggregate(pipeline, projection_model=self.base))

    async def create_function(self, document: dict, **kwargs):
        base = StandardTeam
        team = super().create_function(self, base=base, document=document)
        return team

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

