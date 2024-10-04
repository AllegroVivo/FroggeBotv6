from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import VerificationManager
################################################################################

__all__ = ("VerificationManagerMenuView",)

################################################################################
class VerificationManagerMenuView(FroggeView):

    def __init__(self, owner: User, mgr: VerificationManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            ToggleLogEventsButton(),
            ToggleChangeNameButton(),
            ToggleRequireCaptchaButton(),
            ToggleRequire2FAButton(),
            SetVerifiedRoleButton(),
            RemoveVerifiedRoleButton(),
            AddRelationButton(),
            ModifyRelationButton(),
            RemoveRelationButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddRelationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Role Relation",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyRelationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Role Relation",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveRelationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Role Relation",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_item(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetVerifiedRoleButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Verified Role",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_verified_role(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class RemoveVerifiedRoleButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.secondary,
            label="Remove Verified Role",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_verified_role(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleLogEventsButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Event Logging",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_logging(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleRequireCaptchaButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Captcha",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_captcha(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleRequire2FAButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle 2FA",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_2fa(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleChangeNameButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Change Name",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_change_name(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
