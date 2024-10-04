from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ReactionRole
################################################################################

__all__ = ("ReactionRoleStatusView",)

################################################################################
class ReactionRoleStatusView(FroggeView):

    def __init__(self, owner: User, role: ReactionRole):
        
        super().__init__(owner, role)
        
        button_list = [
            SetLabelButton(),
            SetRoleButton(),
            SetEmojiButton(),
            RemoveEmojiButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetLabelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Label",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.label)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_label(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Role",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._role.id)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_role(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetEmojiButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Emoji",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.emoji)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_emoji(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveEmojiButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Emoji",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.emoji

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_emoji(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
