import discord
from beanie import PydanticObjectId

from engines.shared import *
from engines.base import BaseEngine
from models import SearchOutputType
from models.games import GameBase, AllTeamNamesByGame, Game
from pydantic import ValidationError, BaseModel
from typing import TypeVar, Type, Optional, Literal, Callable, Any, Union, AsyncGenerator, NamedTuple
from beanie.operators import RegEx, Eq
from monggregate import Pipeline

B = TypeVar('B', bound=GameBase)
E = TypeVar('E', bound=BaseEngine)


class GameNames(BaseModel):
    name: str


class GameEngine(BaseEngine):
    base = GameBase

    @BaseEngine.embed_maker
    async def embed_maker(self,
                          embeds: Embeds,
                          item: Type[B] = None,
                          private: Optional[bool] = False) -> list[discord.Embed]:
        if not item: # this means its a dashboard
            embed = embeds.public
            embed.title="Games Dashboard"
            embed.description="Options for managing League Games"
            return [embed]
        else:  # this means theres an item to render
            embed = embeds.public
            embed.title = item.name
            embed.description = item.description
            embed.set_thumbnail(url=item.thumbnail) if item.thumbnail else 0

            teams = ''.join([f"`{team.name}` " for team in item.teams])
            players = ''.join([f"`{player.name}` " for player in item.players])

            embed.add_field(name='Teams', value=teams)
            embed.add_field(name='Players', value=players)
            if private:
                pembed = embeds.private
                pembed.title = f'{item.name} - Private View'
                pembed.description = 'This embed should contain private meta data for admins'
                pembed.set_thumbnail(url=item.thumbnail) if item.thumbnail else 0

                pembed.add_field(name='Total Bans', value='`Not Implemented`')
                pembed.add_field(name='Total Suspensions', value='`Not Implemented`')
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
    async def find_by_modal(self, /,
                            modal: discord.ui.Modal)-> discord.ui.Modal:
        """ You will recieve a view, just add all of your custom inputs and return it   """
        modal.add_item(StandardInput(label='name', placeholder='Leave Blank for ALL'))
        return modal


    @BaseEngine.create_modal
    async def create_modal(self,/, modal: discord.ui.Modal) -> discord.ui.Modal:
        """ used to return a modal instance, add your relevant items """
        items = [StandardInput(label='name', placeholder='Enter the Game Name', required=True),
                 StandardInput(label='description', placeholder='Short description of the game', required=True),
                 StandardInput(label='thumbnail', placeholder='link to the image thumbnail'),
                 StandardInput(label='link', placeholder='link, if any')]
        [modal.add_item(x) for x in items]
        return modal

    @BaseEngine.carousel
    async def carousel(self, /, carousel: CarouselView) -> CarouselView:
        (carousel.add_item(UpdateButton()).add_item(DeleteButton()))
        return carousel

    # SEARCH METHODS
    def get_teams_by_game(self, name: Optional[str] = None) -> type[AsyncGenerator, int]:
        x = AllTeamNamesByGame.find(RegEx('_id', f'(?i){name if name else ""}'))
        return self.results_cursor(x) #TODO: this may be obsolete

    def get_by(self, *,
               name: Optional[str] = None,
               id: Optional[PydanticObjectId] = None) -> Result:
        """ Used to do a query """
        base = GameEngine.base
        search = base.find({}, with_children=True)
        if id:
            search = search.find(Eq(base.id, id))
        if name:
            search = search.find(RegEx(base.name, name, 'i'))
        pipeline = (Pipeline()
                    .lookup(right="TeamBase", left_on='_id', right_on='game.$id', name='teams')
                    .lookup(right="PlayerBase", left_on='_id', right_on='games.$id', name='players')
                    .export())
        return self.results_cursor(search.aggregate(pipeline, projection_model=base))

    # CREATE METHODS
    async def create_function(self, document: dict, **kwargs):
        base = Game
        team = super().create_function(self, base=base, document=document)
        return team

    # NOTHING BELOW IS IMPLEMENTED