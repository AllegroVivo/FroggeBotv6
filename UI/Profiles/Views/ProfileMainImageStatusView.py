from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileImages
################################################################################

__all__ = ("ProfileMainImageStatusView",)

################################################################################
class ProfileMainImageStatusView(FroggeView):

    def __init__(self, owner: User, images: ProfileImages):
        
        super().__init__(owner, images)
        
        button_list = [
            SetMainImageButton(),
            RemoveMainImageButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetMainImageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Set Main Image",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_main_image(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.main_image_status(), view=self.view
        )
        
################################################################################
class RemoveMainImageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Main Image",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = not self.view.ctx.main_image
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_main_image(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.main_image_status(), view=self.view
        )
        
################################################################################
