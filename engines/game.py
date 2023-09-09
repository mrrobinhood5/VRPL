from engines import *
from pydantic import ValidationError
from typing import TypeVar, Type, Optional

base = GameBase
B = TypeVar('B', bound=GameBase)


class GameEngine(BaseEngine):

    async def create_game(self, base: Type[B] = Game, **kwargs) -> Type[B]:
        try:
            game = await base(**kwargs).insert()
            return game
        except ValidationError as e:
            raise e
