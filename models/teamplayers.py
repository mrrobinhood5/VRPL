from typing import Optional

from models.teams import TeamModel
from models.players import PlayerModel


class FullTeamModel(TeamModel):
    captain: PlayerModel
    co_captain: Optional[PlayerModel]
    members: list[PlayerModel]

    class Config:
        schema_extra = {
            "example": {
                "_id": "abc123456789",
                "team_motto": "We are Great!",
                "team_logo": "http://logos.com/img.jpg",
                "active": True,
                "team_mmr": 0,
                "captain": {
                    "_id": "abc123456789",
                    "name": "captain name",
                    "discord_id": "987654321",
                    "game_uid": "abc123abc123",
                    "calibrated_height": "72 in"
                },
                "co_captain": {
                    "_id": "abc123456789",
                    "name": "captain name",
                    "discord_id": "987654321",
                    "game_uid": "abc123abc123",
                    "calibrated_height": "72 in"
                },
                "members": [
                    {
                        "_id": "abc123456789",
                        "name": "captain name",
                        "discord_id": "987654321",
                        "game_uid": "abc123abc123",
                        "calibrated_height": "72 in"
                    },
                    {
                        "_id": "abc123456789",
                        "name": "captain name",
                        "discord_id": "987654321",
                        "game_uid": "abc123abc123",
                        "calibrated_height": "72 in"
                    }
                ]

            }
        }
