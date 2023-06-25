from typing import Optional

from models.teams import TeamModel
from models.players import PlayerModel


class FullTeamModel(TeamModel):
    captain: PlayerModel
    co_captain: Optional[PlayerModel]
    members: list[PlayerModel]

    @property
    def captain_discord_id(self):
        return self.captain.discord_id

    @property
    def co_captain_discord_id(self):
        return None if not self.co_captain else self.co_captain.discord_id


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
                    "discord_id": 1234567890,
                    "game_uid": "abc123abc123",
                    "calibrated_height": "72 in"
                },
                "co_captain": {
                    "_id": "abc123456789",
                    "name": "captain name",
                    "discord_id": 1234567891,
                    "game_uid": "abc123abc123",
                    "calibrated_height": "72 in"
                },
                "members": [
                    {
                        "_id": "abc123456789",
                        "name": "captain name",
                        "discord_id": 1234567890,
                        "game_uid": "abc123abc123",
                        "calibrated_height": "72 in"
                    },
                    {
                        "_id": "abc123456789",
                        "name": "captain name",
                        "discord_id": 1234567890,
                        "game_uid": "abc123abc123",
                        "calibrated_height": "72 in"
                    }
                ]

            }
        }
