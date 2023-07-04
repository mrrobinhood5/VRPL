from typing import Optional, Type
import discord

from models.admin import Base

from views.buttons import ControlButton, CounterButton, UpdateButton, ApproveButton, RejectButton


class UpdateGenericModal(discord.ui.Modal):
    def __init__(self, view: discord.ui.View):
        self.view = view
        super().__init__()

    async def on_error(self, inter: discord.Interaction, error: Exception, item: discord.ui.Item) -> None:
        await inter.edit_original_response(content=f'Error: {error} in {item}', embed=None)


class ItemView(discord.ui.View):

    def __init__(self, items: Optional[list[Base]], modal: UpdateGenericModal):
        super().__init__()
        self.items = items
        self.update = UpdateButton(modal=modal)

        self.updated_item: Optional[Base] = None
        self.add_item(self.update) # Adds the Update Button

    async def on_timeout(self) -> None:
        for child in self.children:
            self.remove_item(child)
        return

    # async def on_error(self, inter: discord.Interaction, error: BaseException, item: discord.ui.Item) -> None:
    #     await inter.response.send_message(content=f'Error: {error} in {item}', embed=None)

    async def interaction_check(self, inter: discord.Interaction) -> bool:
        """ This is used to check if the User who clicks a button is the one who sent it
        Should not be used since most of these are sent ephemeral """
        return True

    async def callback(self, inter: discord.Interaction):
        """ Callback for when the Update Button is Finished
         Overwrite to cater to the item Model (TeamModel or PlayerModel)"""
        raise NotImplemented


class Carousel(ItemView):

    def __init__(self, items: Optional[list[Base]], modal: Optional[UpdateGenericModal]):
        super().__init__(items=items, modal=modal)
        self.item_index = 0
        self.timeout = None

        self.previous = ControlButton('previous')
        self.counter = CounterButton()
        self.next = ControlButton('next')
        self.update.disabled = True

        self.add_item(self.previous).add_item(self.counter).add_item(self.next)

    @property
    def item(self) -> Base:
        return self.items[self.item_index]

    @property
    def item_count(self):
        return len(self.items)

    @property
    def next_item(self):
        self.item_index = (self.item_index + 1) % self.item_count
        yield self.items[self.item_index]

    @property
    def prev_item(self):
        self.item_index = (self.item_index - 1) % self.item_count
        yield self.items[self.item_index]

    @staticmethod
    def is_mine(inter: discord.Interaction, item: Base) -> bool:
        """ override this for the type of check, this should be used to see if you own the item
        to activate the Update Button """
        return NotImplemented

    async def update_view(self, inter: discord.Interaction, item: Base):
        """ calls the item's private_embed to update the view """
        await inter.response.edit_message(embed=item.public_embed(), view=self)


class ConfirmationView(discord.ui.View):

    def __init__(self):
        self.approval = None
        super().__init__()
        self.add_item(ApproveButton(label="Yes"))
        self.add_item(RejectButton(label="No"))

    async def callback(self, inter: discord.Interaction):
        self.stop()
