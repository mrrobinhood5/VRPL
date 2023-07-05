from bson.objectid import ObjectId
from pydantic import Field, validator, FileUrl
from typing import Optional, Union
from pydantic_mongo import ObjectIdField, AbstractRepository
from database import DBConnect
from models.players import PlayerModel
from models.admin import Base
import discord
from views.shared import Carousel, UpdateGenericModal
from config import DEFAULT_TEAM_LOGO
from views.shared import ConfirmationView, UpdateButton
import models


#
# TEAM MODELS
#
class TeamModel(Base):
    """ Team Model is the representation of a full team. In code, it will include full members
    in database it will only include ObjectIDs"""
    id: ObjectIdField = None
    name: str
    motto: str
    logo: Optional[FileUrl]
    captain: Union[PlayerModel, ObjectIdField]
    co_captain: Optional[PlayerModel]
    active: bool = True
    mmr: int = 0
    members: Optional[Union[list[PlayerModel], list[ObjectIdField]]] = Field(default=None, exclude=True)

    @validator('captain')
    def build_captain(cls, v):
        """ takes in a ObjectID and returns the PlayerModel for the Captain """
        if isinstance(v, ObjectId):
            return PlayerModel.get_by_id(v)
        else:
            return v

    @validator('members', each_item=True)
    def build_members(cls, v):
        """ takes in all the member ids and converts then into PlayerModels """
        if isinstance(v, ObjectId):
            return PlayerModel.get_by_id(v)
        else:
            return v

    @classmethod
    def db(cls):
        """ Returns a connection to a collection for this model """
        return TeamsRepo(DBConnect().db)

    def prep_save(self) -> 'Base':  # REFACTOR: This could be clearner
        _updates = {}
        if isinstance(self.captain, PlayerModel):
            _updates.update({'captain': self.captain.id})
        if isinstance(self.co_captain, PlayerModel):
            _updates.update({'co_captain': self.co_captain.id})
        return self.copy(update=_updates)

    def public_embed(self) -> discord.Embed:
        """ Returns the public view Embed for a TeamModel """
        embed = discord.Embed(title=self.name, description=self.motto, color=discord.Color.blurple())
        embed.set_thumbnail(url=self.logo if self.logo else DEFAULT_TEAM_LOGO)
        embed.set_footer(text=f'Active: {self.active}')
        embed.add_field(name="MMR", value=f'```{self.mmr}```', inline=True)
        embed.add_field(name='Captain', value=f'```{self.captain.name}```')
        embed.add_field(name='Co-Captain', value=f'```{self.co_captain.name if self.co_captain else None}```')
        members = f''
        if self.members:
            for member in self.members:
                members += f'`{member.name}` \n'
        embed.add_field(name='Members', value=members)
        return embed

    def private_embed(self) -> discord.Embed:
        """ Returns a private view embed for a TeamModel """
        embed = self.public_embed()
        embed.add_field(name='Warnings', value=f'```Warnings Here```')
        embed.add_field(name='Infractions', value=f'```Infractions Here```')
        return embed

    class TeamCarousel(Carousel):
        def __init__(self, items: Optional[list['TeamModel']]):
            self.modal = TeamUpdateModal(view=self)
            super().__init__(items=items, modal=self.modal)

        @staticmethod
        def is_mine(inter: discord.Interaction, team: 'TeamModel') -> bool:
            if inter.user.id == team.captain.discord_id:
                return True
            if team.co_captain:
                if inter.user.id == team.co_captain.discord_id:
                    return True
            return False


    class PlayerView(discord.ui.View):
        """ PlayerView is what a regular player will see when viewing its own team.
        They can Leave a Team. """

        def __init__(self, team: 'TeamModel'):
            super().__init__()
            self.team = team
            self.updated_item: Optional[TeamModel] = None
            self.msg_for_embed: Optional[discord.Message] = None

        async def finish_off_view(self, inter: discord.Interaction):
            await self.wait()
            self.clear_items()
            msg = await inter.original_response()
            await msg.edit(content=f'Updates Changed', view=self)
            self.stop()

        @discord.ui.button(label='Leave Team', style=discord.ButtonStyle.danger, disabled=False, row=3)
        async def leave_team(self, inter: discord.Interaction, button: discord.ui.Button):
            # send a new msg for confirmation
            await inter.response.defer()
            button.disabled = True

            confirmation = ConfirmationView()  # TODO: Finish the 3 views for teams
            msg = await inter.channel.send(content="Are you Sure?", view=confirmation)
            await confirmation.wait()
            await msg.delete()
            if not confirmation.approval:
                self.stop()
                return

            me = [player.id for player in self.team.members if player.discord_id == inter.user.id][0]
            # await remove_player(str(me))
            # if inter.user.id == self.team.co_captain_discord_id:
            #     await process_team_update(inter, str(self.team.id), UpdateTeamModel(), only_co_captain=True)
            self.stop()

        async def on_error(self, inter: discord.Interaction, error: Exception, item) -> None:
            print(f'{error} called from the view')

    class CoCaptainView(PlayerView):
        """ CoCaptainView is what a CoCaptain will see when viewing his team.
         He can approve joins and remove players, and Update the team along with options in PlayerView """

        def __init__(self, team: 'TeamModel'):
            super().__init__(team=team)
            self.update = self.add_item(UpdateButton(modal=TeamUpdateModal(self)))

        # @button(custom_id='approve_joins', label='Approve Joins', style=ButtonStyle.green, row=2)
        # async def approve_joins(self, inter: Interaction, button: Button):
        #     approvals = await list_pending_approvals(str(self.team.id), full=True)
        #     if approvals:
        #         approvals = [PlayerTeamFullModel(**approval) for approval in approvals]
        #         embed = PlayerEmbed(approvals[0].player)
        #
        #         view = TeamJoinsCarousel(approvals)
        #         await inter.response.send_message(embed=embed, view=view, ephemeral=True)
        #         await view.wait()
        #     else:
        #         await inter.response.send_message(content=f'There are no pending Approvals', delete_after=10)
        #     await self.finish_off_view(inter)
        #
        # @button(label='Remove Player', style=ButtonStyle.danger, disabled=False, row=2)
        # async def remove_player(self, inter: Interaction, button: Button):
        #     options = [SelectOption(label=member.name, value=f'{member.name}:{str(member.id)}')
        #                for member in self.team.members if member.id != self.team.captain.id]
        #     view = MemberChooseView(options=options, team=self.team, choose_type='remove')
        #     await inter.response.send_message(content='Who do you want to remove', view=view, ephemeral=True)
        #     self.stop()

    class CaptainView(CoCaptainView):
        """ CaptainView is what a Captain sees when viewing his own team.
        He has the ability to Destroy a team, Update a CoCaptain along with the rest of
        the views """

        def __init__(self, team: 'TeamModel'):
            super().__init__(team=team)
            self.remove_item(self.leave_team)

        @discord.ui.button(label='Co-Captain', style=discord.ButtonStyle.green, disabled=False, row=1)
        async def update_co_captain(self, inter: discord.Interaction, button: discord.Button):
            button.disabled = True
            if self.team.captain.discord_id != inter.user.id:
                inter.response.send_message(content='You are not Captain of this team :stop_sign:', ephemeral=True)

                self.stop()
            team_captains = [self.team.captain.id, self.team.co_captain.id if self.team.co_captain else None]
            options = [discord.SelectOption(label=member.name, value=f'{member.name}:{str(member.id)}')
                       for member in self.team.members if member.id not in team_captains]
            # view = MemberChooseView(options=options, team=self.team, choose_type='co_captain')
            # await inter.response.send_message(content='Who do you choose as Co-Captain', view=view, ephemeral=True)
            # await self.finish_off_view(inter)

        @discord.ui.button(label='Disband Team', style=discord.ButtonStyle.danger, disabled=False, row=1)
        async def dismantle_team(self, inter: discord.Interaction, button: discord.Button):
            button.disabled = True
            await inter.response.defer()

            confirmation = ConfirmationView()
            msg = await inter.channel.send(content="Are you Sure?", view=confirmation)
            await confirmation.wait()
            await msg.delete()
            if not confirmation.approval:
                self.stop()
                return

            # for player in self.team.members:
            #     await remove_player(str(player.id))

            await inter.response.send(f"Team {self.team.name} has been dismantled.")

    # class MemberChooseDropDown(Select):
    #     def __init__(self, options=list[SelectOption]):
    #         super().__init__(placeholder='Choose a Team Member', min_values=1, max_values=1, options=options)
    #
    #     async def callback(self, inter: Interaction):
    #         self.view.chosen_value = self.values[0].split(':')
    #         await inter.response.send_message(f'`{inter.user.name}` has selected `{self.view.chosen_value[0]}`')
    #         if self.view.choose_type == 'co_captain':
    #             updated_team = UpdateTeamModel(**{'co_captain': self.view.chosen_value[1]})
    #             await process_team_update(inter, str(self.view.team.id), updated_team)
    #         else:
    #             try:
    #                 await remove_player(self.view.chosen_value[1])
    #             except HTTPException as e:
    #                 await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))
    #             else:
    #                 if self.view.chosen_value[1] == str(self.view.team.co_captain.id):
    #                     updated_team = UpdateTeamModel(**{'co_captain': None})
    #                     await process_team_update(inter, str(self.view.team.id), updated_team)
    #         self.view.stop()
    #
    #
    # class MemberChooseView(View):
    #     def __init__(self, options: list[SelectOption], team: FullTeamModel,
    #     choose_type: Literal['co_captain', 'remove']):
    #         super().__init__()
    #         self.team = team
    #         self.choose_type = choose_type
    #         self.add_item(MemberChooseDropDown(options=options))
    #         self.chosen_value = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = False


class TeamsRepo(AbstractRepository[TeamModel]):
    """ This class allows TeamModel to update itself to the db collection """

    class Meta:
        collection_name = 'teams'


#
# TEAM MODALS: Are the Forms sent in Discord to get input from a User
#
class TeamRegisterModal(UpdateGenericModal, title='Register a Team'):
    name = discord.ui.TextInput(label='Team Name', custom_id='name', placeholder='New Team Name', required=True)
    motto = discord.ui.TextInput(label='Team Motto', custom_id='motto', placeholder='Team Motto', required=True)
    logo = discord.ui.TextInput(label='Team Logo URL', custom_id='logo', placeholder='URL for Team Image',
                                required=False, default=None)

    def __init__(self, view: discord.ui.View):  # TODO: can you pass the model you need ot create for on_submit?
        super().__init__(view=view)

    async def on_submit(self, inter: discord.Interaction) -> None:  # TODO: or instead, return everything back to the vie
        """ Called when the form is submitted """
        if TeamModel.get_by_query({'name': self.name.value}):
            raise ValueError('Team Name is already Registered')

        item = TeamModel(name=self.name.value,
                         motto=self.motto.value,
                         logo=self.logo.value or None,
                         captain=PlayerModel.get_by_discord(inter.user))
        self.view.updated_item = item
        if not (result := item.save()):
            raise ValueError('Team could not be saved')

        c = models.PlayerTeamLinkModel(player=PlayerModel.get_by_discord(inter.user), team=item, approved=True)
        c.save()
        await inter.response.send_message(f'{"Success" if result else "Error!!"}', ephemeral=True)
        self.stop()


class TeamUpdateModal(TeamRegisterModal, title='Team Update'):

    def __init__(self, view: discord.ui.View) -> None:
        super().__init__(view=view)
        for text_input in self.children:
            text_input.required = False

    async def on_submit(self, inter: discord.Interaction) -> None:
        updates = {x.custom_id: x.value for x in self.children if x.value} # noqa
        self.view.updated_item = self.view.item.copy(update=updates, deep=True) if updates else None
        await inter.response.send_message(f'Updates have been sent', delete_after=10)


#
# TEAM PERSISTENT VIEWS
#
class TeamChooseDropdown(discord.ui.Select):
    def __init__(self, options=list[discord.SelectOption]):
        super().__init__(placeholder='Choose a Team', min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        self.view.team_value = self.values[0].split(':')
        await inter.response.send_message(f'`{inter.user.name}` has requested to join `{self.view.team_value[1]}`')
        self.view.stop()


class TeamChooseView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__()
        self.add_item(TeamChooseDropdown(options=options))
        self.team_value = None


class TeamRegisterPersistent(discord.ui.View):
    """ This is the main View for the Team registration and Joins """

    def __init__(self):
        super().__init__(timeout=None)
        self.updated_item: Optional[TeamModel] = None

    async def on_error(self, inter: discord.Interaction, error: Exception, item: Optional[discord.ui.Item] = None):
        await inter.response.send_message(content=f'{error}', ephemeral=True)

    @discord.ui.button(label='Register a Team', style=discord.ButtonStyle.green, custom_id='team:register')
    async def register(self, inter: discord.Interaction, button: discord.ui.Button):

        if not (player := PlayerModel.get_by_discord(inter.user)):
            raise ValueError(f'You are not registered yet.')
        if models.PlayerTeamLinkModel.get_approved(inter.user):
            raise ValueError(f'You already belong to a team')

        modal = TeamRegisterModal(view=self)

        await inter.response.send_modal(modal)
        await modal.wait()
        await inter.channel.send(content="**New Team Registered**", embed=self.updated_item.public_embed())

    @discord.ui.button(label="Join a Team", style=discord.ButtonStyle.blurple, custom_id='team:join')
    async def join(self, inter: discord.Interaction, button: discord.ui.Button):
        if not (player := PlayerModel.get_by_discord(inter.user)):
            await inter.response.send_message(content="You are not registered", ephemeral=True)
        # try:  # check to see if this player does not already belong to a team
        #         player_team = await get_player_team(inter.user.id)
        #     except HTTPException as e:  # doesn't belong to team
        #         teams = await list_teams()
        #         teams = [TeamModel(**team) for team in teams]
        #         options = [SelectOption(label=team.name, value=f'{str(team.id)}:{team.name}',
        #                                 description=team.team_motto)
        #                    for team in teams if team.active]
        #         view = TeamChooseView(options=options)
        #         await inter.response.send_message(content='Where do you want to send your request?', view=view,
        #                                           ephemeral=True)
        #
        #         await view.wait()
        #         view.clear_items()
        #         msg = await inter.original_response()
        #         await msg.edit(content=f'Request Sent!', view=view)
        #         try:
        #             await request_to_join_team(view.team_value[0], PlayerTeamModel(**{"player": player['_id']}))
        #         except HTTPException as e:  # will error out if a similar request has been submitted
        #             await inter.channel.send(embed=GenericErrorEmbed(inter.user, e))
        #
        #         # Send DM to both captain and co-captain
        #         team = FullTeamModel(**await show_team(view.team_value[0], full=True))
        #         await inter.guild.get_member(team.captain.discord_id).send(f'{inter.user.name} requested to join your team. use `/team my_team` to approve this')
        #         if team.co_captain:
        #             await inter.guild.get_member(team.co_captain.discord_id).send(f'{inter.user.name} requested to join your team. use `/team my_team` to approve this')
        #     else:  # player already belongs to team
        #         await inter.response.send_message(content=f'You already belong to {player_team["name"]}',
        #                                           ephemeral=True)

    def embed(self) -> discord.Embed:
        embed = discord.Embed(title="Team Registration", description="Click below to register a team")
        embed.add_field(name='Registrations',
                        value=f'By registering a team, you are opening up sign-ups for your team. Only a Captain / '
                              f'Co-Captain can approved the team join requests')
        embed.add_field(name='Team Name', value=f'You will be submitting the proper name for your team')
        embed.add_field(name='Team Motto', value=f'This will be the text used to describe your team. ')
        embed.add_field(name='Team Logo',
                        value=f'You can use an imgur link or a discord link to provide the team URL')
        embed.set_image(url='https://i.imgur.com/34eBdG2.png')
        embed.set_thumbnail(url='https://i.imgur.com/VwQoXMB.png')
        return embed
