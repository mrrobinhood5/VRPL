from engines import *
from engines.base import BaseEngine
from models.games import GameBase
from pydantic import ValidationError, BaseModel
from typing import TypeVar, Type, Optional
from beanie.operators import RegEx


base = GameBase
B = TypeVar('B', bound=GameBase)

class GameShortView(BaseModel):
    name: str

class GameEngine(BaseEngine):

    def __init__(self):
        BaseEngine.ge = self

    async def get_one_by_name(self, name: str) -> Optional[B]:
        return await base.find(RegEx(base.name, f'(?i){name}'), with_children=True, fetch_links=True).first_or_none()

    async def get_by_name(self, name: str) -> Optional[list[B]]:
        return await base.find(RegEx(base.name, f'(?i){name}'), with_children=True, fetch_links=True).to_list()

    async def all_games_names(self) -> list:
        return await base.find({}, with_children=True).project(GameShortView).to_list()

    async def create_game(self, base: Type[B] = Game, **kwargs) -> Type[B]:
        try:
            game = await base(**kwargs).insert()
            return game
        except ValidationError as e:
            raise e

