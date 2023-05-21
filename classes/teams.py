from dataclasses import field
from pydantic import HttpUrl
from classes.base import Base, PyObjectId
from typing import Union, List, Optional
from classes.errors import TeamError, TournamentError
from transactions.transaction_log import TransactionType


class TeamModel(Base):
    team_motto: str
    captain: PyObjectId
    team_logo: Optional[HttpUrl]
    co_captain: Optional[PyObjectId]
    active: bool = True
    team_mmr: int = 0

    class Config:
        schema_extra = {
            "example": {
                "name": "Team Name",
                "captain": "ObjectID",
                "team_motto" : "We are Great!"
            }
        }

    # def __init__(self, description: str, id: PydanticObjectId = field(default_factory=PydanticObjectId), *args,
    #              **kwargs):
    #
    #     super().__init__(*args, **kwargs)
    #     self.description = description
    #     self.id = id
    #
    # def __post_init__(self):
    #     # Check to see if the team name is not duplicate
    #     if isinstance(Team.instances(), List):
    #         if self.name in [x.name for x in Team.instances()]:
    #             raise TeamError('Team name is already in use')
    #
    #     self.logger.log(TransactionType.TEAM_CREATE, requestor=Player.lookup(self.captain), obj=self)
    #
    #     # Add captain to the team
    #     Player.lookup(self.captain).join_team(self)
    #
    #     self.__class__._instances.append(self)
    #
    # def join_tournament(self, requestor: PydanticObjectId, tournament: 'Tournament'):
    #     # check to see who requested it, make sure its captain
    #     if requestor is not self.captain:
    #         raise TournamentError('You are not the captain')
    #
    #     # check oto see if tournament is active
    #     if not tournament.active:
    #         raise TournamentError('That\'s not a valid tournament ID')
    #
    #     # check the tournament passed if its individual. If so, team cannot be created.
    #     if tournament.individual:
    #         raise TournamentError('This is not a team tournament')
    #
    #     # check to see if the team is already in
    #     if self in tournament.teams:
    #         raise TournamentError('You are already in this tournament')
    #
    #     self.logger.log(TransactionType.TOURNAMENT_JOIN,
    #                     requestor=self,
    #                     obj=tournament)
    #
    #     self.belongs_to_tournament.append(tournament)
    #
    #     return True
    #
    # @property
    # def team_full(self) -> bool:
    #     if isinstance(Player.instances(), List):
    #         _ = len([x for x in Player.instances() if self in x.belongs_to_team])
    #         return True if _ >= 10 else False
    #     else:
    #         return False
    #
    # @property
    # def player_count(self) -> int:
    #     return len([x for x in Player.instances() if self in x.belongs_to_team])
    #
    # @property
    # def players(self) -> List:
    #     if isinstance(Player.instances(), List):
    #         return [x for x in Player.instances() if self in x.belongs_to_team]
    #     elif Player.instances().belongs_to_team == self:
    #         return [Player.instances()]
    #     else:
    #         return []
    #
    # def make_co_captain(self, requestor: PydanticObjectId, co_captain: PydanticObjectId) -> bool:
    #     # check to see if requestor is the captain
    #     if requestor is not self.captain:
    #         raise TeamError("You are not captain, not allowed to make changes")
    #
    #     # check to see if co_captain is in the team
    #     if co_captain not in [x.id for x in self.players]:
    #         raise TeamError("That Player is not on this team")
    #
    #     # check to see if captain is not co-captain
    #     if co_captain is self.captain:
    #         raise TeamError("Captain cannot be Co-Captain")
    #
    #     self.co_captain = co_captain
    #
    #     self.logger.log(TransactionType.PLAYER_PROMOTE,
    #                     requestor=Player.lookup(requestor),
    #                     obj=self,
    #                     additional=Player.lookup(co_captain))
    #     return True
    #
    # def kick_player(self, requestor: PydanticObjectId, kicked_player: PydanticObjectId) -> bool:
    #     # implement kick player by a team_captain or co-captain
    #     pass
    #
    # @property
    # def matches(self):
    #     # implement a count of how many matches the team has played
    #     return True
    #
    # @property
    # def to_dict(self):
    #     _r = {
    #         'id': str(self.id),
    #         'name': self.name,
    #         'description': self.description,
    #         'captain': str(self.captain),
    #         'belongs_to_division': str(self.belongs_to_division.id),
    #         'co_captain': None or str(self.co_captain),
    #         'belongs_to_tournament': [str(x.id) for x in self.belongs_to_tournament],
    #         'active': self.active,
    #         'team_full': self.team_full,
    #         'player_count': self.player_count,
    #         'players': [str(x.id) for x in self.players]
    #     }
    #     return _r


class UpdateTeamModel(Base):
    name: Optional[str]
    team_motto: Optional[str]
    captain: Optional[PyObjectId]
    team_logo: Optional[HttpUrl]
    co_captain: Optional[PyObjectId]
    active: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "name": "New Team Name",
                "team_motto": "We are still great!",
                "captain": "ObjectID",
                "co_captain": "ObjectID",
                "active": True
            }
        }
