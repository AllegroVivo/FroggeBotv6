from __future__ import annotations

from typing import TYPE_CHECKING, Union

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import SecondaryElement, TemplateSecondary
################################################################################

__all__ = ("EventElementStatusView",)

################################################################################
class EventElementStatusView(FroggeView):

    def __init__(self, owner: User, element: Union[SecondaryElement, TemplateSecondary]):
        
        super().__init__(owner, element)
        
        button_list = [
            SetTitleButton(),
            SetValueButton(),
            RemoveElementButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class SetTitleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Title",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_title(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetValueButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Value",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_value(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveElementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Element",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        if not await self.view.ctx.remove(interaction):
            return
        
        self.view.complete = True
        await self.view.stop()  # type: ignore
        
################################################################################
