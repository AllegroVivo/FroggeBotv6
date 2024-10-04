from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VIPManager
################################################################################

__all__ = ("VIPMessageManagementView",)

################################################################################
class VIPMessageManagementView(FroggeView):

    def __init__(self, owner: User, mgr: VIPManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            WarningMsgManagementButton(),
            ExpiryMsgManagementButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class WarningMsgManagementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Manage Renewal Message",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.warning_message_management(interaction)
        
################################################################################
class ExpiryMsgManagementButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Manage Expiration Message",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.expiry_message_management(interaction)

################################################################################
