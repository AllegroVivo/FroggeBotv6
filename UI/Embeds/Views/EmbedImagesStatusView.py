from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import FroggeEmbedImages
################################################################################

__all__ = ("EmbedImagesStatusView",)

################################################################################
class EmbedImagesStatusView(FroggeView):

    def __init__(self, owner: User, images: FroggeEmbedImages):
        
        super().__init__(owner, images)
        
        button_list = [
            SetThumbnailButton(),
            RemoveThumbnailButton(),
            SetMainImageButton(),
            RemoveMainImageButton(),
            CloseMessageButton(),
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetThumbnailButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Thumbnail",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_thumbnail(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveThumbnailButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Thumbnail",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.thumbnail is None

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_thumbnail(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )

################################################################################
class SetMainImageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Main Image",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_main_image(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveMainImageButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Main Image",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.disabled = self.view.ctx.main_image is None

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_main_image(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )

################################################################################
