from discord.ui import View, Modal
from discord import Message, Interaction, Embed
from models.base import Base
from typing import Optional
from views.buttons import ControlButton, CounterButton, UpdateButton


class Carousel(View):

    def __init__(self, items: Optional[list[Base]], modal: Optional[Modal]):
        super().__init__()
        self.modal = modal
        self.items = items
        self.item_index = 0
        self.timeout = None
        self.updated_item: Optional[Base] = None
        self.msg_for_embed: Optional[Message] = None

        self.previous = ControlButton('previous')
        self.counter = CounterButton()
        self.next = ControlButton('next')
        self.update = UpdateButton(self.modal, disabled=True)

        self.add_item(self.previous).add_item(self.counter).add_item(self.next).add_item(self.update)

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
    def is_mine(inter: Interaction, item: Base) -> bool:
        """ override this for the type of check """
        return NotImplemented

    async def update_view(self, inter: Interaction, item: Base):
        """ override this for the embed type """
        # await inter.response.edit_message(embed=Embed(item), view=self)
        return NotImplemented
