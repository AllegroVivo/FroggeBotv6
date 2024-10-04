from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, User, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfileImages
################################################################################

__all__ = ("ProfileImagesStatusView",)

################################################################################        
class ProfileImagesStatusView(FroggeView):

    def __init__(self, user: User, images: ProfileImages):

        super().__init__(user, images)

        button_list = [
            ManageThumbnailButton(),
            ManageMainImageButton(),
            AddAdditionalImageButton(),
            ManageAdditionalImagesButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()

################################################################################        
class ManageThumbnailButton(FroggeButton):

    def __init__(self) -> None:

        super().__init__(
            style=ButtonStyle.primary,
            label="Manage Thumbnail",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.thumbnail_management(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=self.view.ctx.status(), view=self.view
        )

################################################################################
class ManageMainImageButton(FroggeButton):
    
    def __init__(self) -> None:
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Manage Main Image",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.main_image_management(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddAdditionalImageButton(FroggeButton):
    
    def __init__(self) -> None:
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Additional Image",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.add_additional_image(interaction)
        await self.view.edit_message_helper(
            interaction=interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ManageAdditionalImagesButton(FroggeButton):
    
    def __init__(self) -> None:
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Manage Additional Images",
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.additional) == 0
        
    async def callback(self, interaction: Interaction) -> None:
        await self.view.ctx.paginate_additional(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction=interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
