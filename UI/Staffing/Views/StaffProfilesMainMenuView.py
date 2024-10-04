from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, TextChannel, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton
from Utilities.Constants import *

if TYPE_CHECKING:
    from Classes import StaffMember
################################################################################

__all__ = ("StaffProfilesMainMenuView",)

################################################################################
class StaffProfilesMainMenuView(FroggeView):

    def __init__(self, owner: User, staff: StaffMember):
        
        super().__init__(owner, staff)
        
        button_list = [
            AddCharacterButton(),
            ModifyCharacterButton(),
            RemoveCharacterButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class AddCharacterButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Character",
            disabled=False,
            row=0
        )
        
    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.characters) == MAX_CHARACTERS_PER_STAFF
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_character(interaction)
        self.view.set_button_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.profile_main_status(), view=self.view
        )

################################################################################
class ModifyCharacterButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Character",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.characters) == 0

    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_character(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.profile_main_status(), view=self.view
        )

################################################################################
class RemoveCharacterButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Character",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.disabled = len(self.view.ctx.characters) == 0

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_character(interaction)
        self.view.set_button_attributes()

        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.profile_main_status(), view=self.view
        )
        
################################################################################
