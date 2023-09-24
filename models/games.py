from models.base import GameBase, VRPLObject, PlayerBase, TeamBase, CasterBase, MapBase, TournamentBase
from beanie import Link, View
from pydantic import Field
from monggregate import Pipeline, S
from monggregate.operators import first


class Game(GameBase):
    ...


class AllTeamNamesByGame(View):
    name: str = Field(alias='_id')
    teams: list[str]
    description: str

    class Settings:
        source = TeamBase

        pipeline = (Pipeline()
                    .lookup(right='GameBase', right_on='_id', left_on='game.$id', name='game')
                    .unwind('$game')
                    .group(by='$game.name', query={'teams': S.push('$name'), 'description': first('$game.description')})
                    .export())
