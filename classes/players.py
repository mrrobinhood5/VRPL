from pydantic import EmailStr, Field
from typing import Optional
from classes.base import Base, PyObjectId


class PlayerModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    discord_id: str  # figure out how to validate this
    game_uid: str  # figure out how to validate this
    calibrated_height: str
    promo_email: Optional[EmailStr]

    is_banned: bool = False
    is_suspended: bool = False
    player_mmr: int = 0

    class Config:
        schema_extra = {
            "example": {
                "name": "MrRobinhood5",
                "discord_id": "DISCORD_ID",
                "game_uid": "1234567890",
                "calibrated_height": "5ft 6in",
            }
        }


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
                "game_uid": "1234567890",
                "calibrated_height": "5ft 6in"
            }
        }


class PlayerTeamModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    player: PyObjectId
    name: Optional[str]
    team: Optional[PyObjectId]
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
