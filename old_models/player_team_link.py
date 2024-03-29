import discord
from old_models.base import Base
from old_models.players import PlayerModel
from old_models.teams import TeamModel
from pydantic_mongo import ObjectIdField, AbstractRepository
from pydantic import validator
from views.shared import Carousel, ApproveButton, RejectButton
from database import Database
from bson import ObjectId
from typing import Optional, Union


#
# PLAYER TEAM LINKS
#
class PlayerTeamLinkModel(Base):
    """ PlayerTeamLinkModel stores the links between players and teams.
    This is essentially the TeamJoin Approvals """
    id: ObjectIdField = None
    player: Union[ObjectIdField, PlayerModel]
    team: Union[ObjectIdField, TeamModel]
    approved: bool = False

    @validator('player')
    def convert_player(cls, v):
        if isinstance(v, ObjectId):
            return PlayerModel.get_by_id(v)
        return v

    @validator('team')
    def convert_team(cls, v):
        if isinstance(v, ObjectId):
            return TeamModel.get_by_id(v)
        return v

    def prep_save(self) -> 'Base':
        _updates = {}
        if isinstance(self.player, PlayerModel):
            _updates.update({'player': self.player.id})
        if isinstance(self.team, TeamModel):
            _updates.update({'team': self.team.id})
        return self.copy(update=_updates)

    @classmethod
    def get_approved(cls, player: discord.Member) -> Optional['PlayerTeamLinkModel']:
        """ given a player discord member, it will return a PlayerTeamLinkModel if there are any approved joins"""
        _ = PlayerModel.get_by_discord(player)
        return PlayerTeamLinkModel.get_one_by_query({'player': _.id, 'approved': True})

    @classmethod
    def db(cls):
        """ Returns a connection to a collection for this model """
        return PlayerTeamLinkRepo(Database().db)

    class ApprovalsCarousel(Carousel):
        def __init__(self, items: Optional[list['PlayerTeamLinkModel']]):
            super().__init__(items=items, modal=None)
            self.remove_item(self.update)
            self.add_item(ApproveButton()).add_item(RejectButton())
            self.approval = None

        @staticmethod
        def is_mine(inter: discord.Interaction, item):
            """ This normally checks to see if the update button gets turned on, but doesn't apply here"""
            return True

        async def callback(self, inter: discord.Interaction):
            """ Called when approve or Reject Button are pressed. Should do the save or update"""
            if self.approval: # TODO:Why the fuck cant the button do this shit instead of passing back?
                updates = {'approved': True}
                new_item = self.item.copy(update=updates)
                results = new_item.save()
                # process the approval

                # remove this item from the self.items

                # move to the next one if there are more

                # if no more post the full team as an update in the teams channel
                self.stop()
            else:
                result = self.item.delete()
            self.stop()

    class Config:
        json_encoders = {ObjectId: str}


class PlayerTeamLinkRepo(AbstractRepository[PlayerTeamLinkModel]):
    """ This class allows PlayerTeamLinkModels to update itself to the db collection """
    class Meta:
        collection_name = 'player_team_link'
