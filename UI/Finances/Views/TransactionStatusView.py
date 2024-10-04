from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Transaction
################################################################################

__all__ = ("TransactionStatusView",)

################################################################################
class TransactionStatusView(FroggeView):

    def __init__(self, owner: User, transaction: Transaction):
        
        super().__init__(owner, transaction)
        
        button_list = [
            SetAmountButton(),
            SetCategoryButton(),
            SetMemoButton(),
            SetTagsButton(),
            CloseMessageButton(),
            ToggleVoidButton(),
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetAmountButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Amount",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_amount(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetCategoryButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Category",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_category(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetMemoButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Memo",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_memo(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetTagsButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Tags",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_tags(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleVoidButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            disabled=False,
            row=4
        )

    def set_attributes(self) -> None:
        self.label = (
            "Unvoid Transaction"
            if self.view.ctx.void
            else "Void Transaction"
        )
        self.style = (
            ButtonStyle.primary
            if self.view.ctx.void
            else ButtonStyle.danger
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_void(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
