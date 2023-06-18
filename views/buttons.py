from discord.ui import Button, Modal
from discord import ButtonStyle, Interaction
from typing import Optional, Literal


class ControlButton(Button):

    def __init__(self, custom_id: Literal['next', 'previous']):
        if custom_id == 'next':
            label = "Next >"
        else:
            label = "< Previous"
        super().__init__(custom_id=custom_id, label=label, style=ButtonStyle.green)

    async def callback(self, inter: Interaction):
        if self.view.is_mine(inter, item := next(self.view.next_item if self.custom_id == 'next' else self.view.prev_item)):
            self.view.update.disabled = False
        else:
            self.view.update.disabled = True
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        await self.view.update_view(inter, item)


class UpdateButton(Button):

    def __init__(self, modal: Modal, disabled: Optional[bool] = False):
        self.modal = modal
        super().__init__(custom_id='update', label='Update', style=ButtonStyle.blurple, disabled=disabled)

    async def callback(self, inter: Interaction):
        await inter.response.send_modal(self.modal)
        await self.modal.wait()
        await self.view.callback(inter)
        self.view.stop()


class CounterButton(Button):

    def __init__(self):
        super().__init__(custom_id='counter', label='1 of x', style=ButtonStyle.grey)

    async def callback(self, inter: Interaction):
        self.view.counter.label = f'{self.view.item_index + 1} of {self.view.item_count}'
        await inter.response.edit_message(view=self.view)


class ApproveButton(Button):

    def __init__(self):
        super().__init__(custom_id='approve', label='Approve', style=ButtonStyle.green)

    async def callback(self, inter: Interaction):
        self.view.approval = True
        await self.view.callback(inter)
        self.view.stop()


class RejectButton(Button):

    def __init__(self):
        super().__init__(custom_id='reject', label='Reject', style=ButtonStyle.danger)

    async def callback(self, inter: Interaction):
        self.view.approval = False
        await self.view.callback(inter)
        self.view.stop()
