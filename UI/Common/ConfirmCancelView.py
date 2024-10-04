from __future__ import annotations

from typing import Union, Literal

from discord import ButtonStyle, Interaction, Member, User
from discord.ui import Button

from .FroggeView import FroggeView
################################################################################

__all__ = ("ConfirmCancelView",)

################################################################################
class ConfirmCancelView(FroggeView):

    def __init__(
        self, 
        owner: Union[Member, User],
        return_interaction: bool = False,
        show_cancel: bool = True,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        **kwargs
    ):
        
        self.return_interaction: bool = return_interaction
        super().__init__(owner, None, **kwargs)

        self.add_item(ConfirmCancelButton(confirm_text, 1))
        if show_cancel:
            self.add_item(ConfirmCancelButton(cancel_text, 2))

################################################################################
class ConfirmCancelButton(Button):
    
    def __init__(self, text: str, button_type: int):
        
        super().__init__(
            style=(
                ButtonStyle.success 
                if button_type == 1
                else ButtonStyle.danger
            ),
            label=text,
            disabled=False,
            row=0
        )
    
        self._type: int = button_type
        
    async def callback(self, interaction: Interaction):
        self.view.value = (
            True if not self.view.return_interaction
            else (True, interaction)
        ) if self._type == 1 else False
        self.view.complete = True
        
        if self._type == 1 and not self.view.return_interaction:
            await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
