from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, ButtonStyle
from discord.ui import View

from UI.Common import CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import AdditionalImage
################################################################################

__all__ = ("AdditionalImageEditView",)

################################################################################
class AdditionalImageEditView(View):

    def __init__(self, image: AdditionalImage):
        
        super().__init__()
        
        button_list = [
            SetCaptionButton(image.id),
            RemoveImageButton(image.id),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class SetCaptionButton(FroggeButton):
    
    def __init__(self, image_id: str):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Caption",
            disabled=False,
            row=0
        )
        
        self.image_id: str = image_id
        
    async def callback(self, interaction: Interaction):
        image = self.view.ctx.get_additional(self.image_id)
        await image.set_caption(interaction)
        
        await self.view.update(
            pages=[a.page() for a in self.view.ctx.additional],
            current_page=self.view.current_page
        )
        
################################################################################
class RemoveImageButton(FroggeButton):
    
    def __init__(self, image_id: str):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Image",
            disabled=False,
            row=0
        )

        self.image_id: str = image_id
        
    async def callback(self, interaction: Interaction):
        image = self.view.ctx.get_additional(self.image_id)
        await image.remove(interaction)
        
        if len(self.view.ctx.additional) == 0:
            self.view.complete = True
            await self.view.message.delete()
            return

        await self.view.update(
            pages=[a.page() for a in self.view.ctx.additional],
            current_page=self.view.current_page - 1 if self.view.current_page != 0 else 0
        )
        
################################################################################
