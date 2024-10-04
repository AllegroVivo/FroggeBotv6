from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Giveaway
################################################################################

__all__ = ("GiveawayStatusView",)

################################################################################
class GiveawayStatusView(FroggeView):

    def __init__(self, owner: User, giveaway: Giveaway):
        
        super().__init__(owner, giveaway)
        
        button_list = [
            SetNameButton(),
            SetDescriptionButton(),
            SetColorButton(),
            SetPrizeButton(),
            SetThumbnailButton(),
            SetEmojiButton(),
            SetEndDateButton(),
            SetNumWinnersButton(),
            ToggleAutoNotifyButton(),
            PostGiveawayButton(),
            RollWinnersButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Name",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetDescriptionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Description",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_description(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetColorButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Color",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_color(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetPrizeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Prize",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_prize(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
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
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetEmojiButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Emoji",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_emoji(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetEndDateButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set End Date",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_end_date(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetNumWinnersButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Num. Winners",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_num_winners(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleAutoNotifyButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            disabled=False,
            row=1
        )
        
    def set_attributes(self) -> None:
        self.style = (
            ButtonStyle.success
            if self.view.ctx.auto_notify
            else ButtonStyle.danger
        )
        self.label = (
            "Auto-Notify: On"
            if self.view.ctx.auto_notify
            else "Auto-Notify: Off"
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_auto_notify(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PostGiveawayButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Post Giveaway to Channel",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.post(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RollWinnersButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Roll Winners",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.determine_winners(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
