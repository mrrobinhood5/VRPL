from typing import Optional, Literal

from discord import ButtonStyle, Interaction, Object
from discord.ui import Button, Modal


class ControlButton(Button):

    def __init__(self, action: Literal['next', 'previous']):
        self.action = action
        if action == 'next':
            label = "Next >"
        else:
            label = "< Previous"
        super().__init__(label=label, style=ButtonStyle.green)

    async def callback(self, inter: Interaction):
        # await inter.response.defer()
        if self.view.is_mine(inter, item := next(self.view.next_item if self.action == 'next'
                                                 else self.view.prev_item)):
            self.view.update.disabled = False
        else:
            self.view.update.disabled = True
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        await self.view.update_view(inter, item)


class UpdateButton(Button):

    def __init__(self, modal: Modal, disabled: Optional[bool] = False):
        self.modal = modal
        super().__init__(custom_id='update', label='Update', style=ButtonStyle.blurple, disabled=disabled, row=2)

    async def callback(self, inter: Interaction):
        await inter.response.send_modal(self.modal)
        await self.modal.wait()
        await self.view.callback(inter)


class CounterButton(Button):

    def __init__(self):
        super().__init__(custom_id='counter', label='1 of x', style=ButtonStyle.grey)

    async def callback(self, inter: Interaction):
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        await inter.response.edit_message(view=self.view)


class ApproveButton(Button):

    def __init__(self, label: Optional[str] = 'Approve'):
        super().__init__(custom_id='approve', label=label, style=ButtonStyle.green)

    async def callback(self, inter: Interaction):
        self.view.approval = True
        inter = inter if inter else Object(id="1234")
        await self.view.callback(inter) if inter else await self.view.callback()


class RejectButton(Button):

    def __init__(self, label: Optional[str] = 'Reject'):
        super().__init__(custom_id='reject', label=label, style=ButtonStyle.danger)

    async def callback(self, inter: Interaction):
        self.view.approval = False
        await self.view.callback(inter) if inter else await self.view.callback()
