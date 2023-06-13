from models.base import Base, PyObjectId
from pydantic import Field
from typing import Optional


class SettingsModel(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    teams_channel: Optional[int]
    teams_message: Optional[int]
    players_channel: Optional[int]
    players_message: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "players_channel": 1234567890,
                "teams_channel": 1234567890,
                "players_message": 1234567890,
                "teams_message": 1234567890
            }
        }


class UpdateSettingsModel(Base):
    name: Optional[str]
    teams_channel: Optional[int]
    teams_message: Optional[int]
    players_channel: Optional[int]
    players_message: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "players_channel": 1234567890,
                "teams_channel": 1234567890,
                "players_message": 1234567890,
                "teams_message": 1234567890
            }
        }
