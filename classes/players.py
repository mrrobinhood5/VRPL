
from pydantic import EmailStr
from typing import List, Optional
from bson.objectid import ObjectId
from classes.base import Base, PyObjectId

from classes.errors import PlayerError, TournamentError, TeamError
from transactions.transaction_log import TransactionType


class PlayerModel(Base):
    discord_id: str # figure out how to validate this
    game_uid: str # figure out how to validate this
    calibrated_height: str
    promo_email: Optional[EmailStr]

    is_banned: bool = False
    is_suspended: bool = False
    player_mmr: int = 0

    class Config:
        schema_extra = {
            "example": {
                "name" : "MrRobinhood5",
                "discord_id": "DISCORD_ID",
                "game_uid": "abcdefghijklmnop",
                "calibrated_height": "5ft 6in",
            }
        }


    # @property
    # def in_game_name(self):
    #     return self.name
    #
    # def __post_init__(self):
    #     # at some point check to see if the same uid or in_game_name is not in use
    #     if self.game_uid:
    #         if Player.instances() is List:
    #             if self.game_uid in [_.game_uid for _ in Player.instances()]:
    #                 raise PlayerError('UID is already in use.')
    #
    #     # log the player registration
    #     self.logger.log(TransactionType.PLAYER_REGISTER, requestor=self, obj=self)
    #
    #     # add it player to Player instances
    #     self.__class__._instances.append(self)
    #
    # def join_tournament(self, tournament: 'Tournament'):
    #     if tournament.individual:
    #         if not self.belongs_to_tournament:
    #             self.belongs_to_tournament = [tournament]
    #         else:
    #             self.belongs_to_tournament.append(tournament)
    #     else:
    #         raise TournamentError('Cannot join tournament without a team')
    #
    #     # log the tournament join
    #     self.logger.log(TransactionType.TOURNAMENT_JOIN, requestor=self, obj=tournament)
    #
    # def join_team(self, team: 'Team') -> bool:
    #     """
    #     Adds the team object to its teams. It should check to see if the team is full first
    #     :param team:
    #     :return:
    #     """
    #     if team.team_full:
    #         raise TeamError('Cannot join team, max players allowed has been reached')
    #     elif team in self.belongs_to_team:
    #         raise TeamError('You are already part of this team. Doh!')
    #     else:
    #         # log the tournament join
    #         self.logger.log(TransactionType.TEAM_JOIN, requestor=self, obj=team)
    #
    #         self.belongs_to_team.append(team)
    #         return True


class UpdatePlayerModel(Base):
    name: Optional[str]
    promo_email: Optional[EmailStr]
    game_uid: Optional[str]
    calibrated_height: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "New In Game Name",
                "promo_email": "myemail@mydomain.com",
                "game_uid": "abcdefghijklmnop",
                "calibrated_height": "5ft 6in"
            }
        }


class PlayerTeamModel(Base):
    name: Optional[str]
    team: PyObjectId
    player: PyObjectId
    approved: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "team": "ObjectId",
                "player": "ObjectId"
            }
        }


class UpdatePlayerTeamModel(Base):
    name: Optional[str]
    approved: bool

    class Config:
        schema_extra = {
            "example": {
                "approved": True
            }
        }