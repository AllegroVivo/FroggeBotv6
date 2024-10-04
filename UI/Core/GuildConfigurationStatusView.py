from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, TextChannel, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import GuildConfiguration
################################################################################

__all__ = ("GuildConfigurationStatusView",)

################################################################################
class GuildConfigurationStatusView(FroggeView):

    def __init__(self, owner: User, config: GuildConfiguration):
        
        super().__init__(owner, config)
        
        button_list = [
            LogChannelButton(),
            TimezoneButton(),
            ConfigureVerificationButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class LogChannelButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Log Channel",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._log_channel.id)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_log_channel(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class TimezoneButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Timezone",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_timezone(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ConfigureVerificationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Configure Verification Module",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.configure_verification(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
