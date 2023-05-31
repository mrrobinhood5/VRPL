import discord
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


class PlayerEmbed(discord.Embed):

    def __init__(self, player: PlayerModel, user: discord.User):
        super().__init__(title=player.name, description=f'AKA {user.name}')
        self.color = discord.Color.orange()
        self.set_thumbnail(url=user.avatar.url)
        self.set_footer(text=f'Banned: {player.is_banned} | Suspended: {player.is_suspended}')
        self.add_field(name='MMR', value=player.player_mmr, inline=True)
        self.add_field(name='Game UID', value=player.game_uid, inline=True)
        self.add_field(name='Calibrated Height', value=player.calibrated_height, inline=True)

