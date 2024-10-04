from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, TextChannel, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Room
################################################################################

__all__ = ("RoomStatusView",)

################################################################################
class RoomStatusView(FroggeView):

    def __init__(self, owner: User, room: Room):
        
        super().__init__(owner, room)
        
        button_list = [
            SetNameButton(),
            SetOwnerButton(),
            SetThemeButton(),
            SetDescriptionButton(),
            SetEmojiButton(),
            ToggleLockedButton(),
            ToggleDisabledButton(),
            SetIndexButton(),
            AddImageButton(),
            RemoveImageButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Name",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.name)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_name(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetOwnerButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Owner",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx._details._owner.id)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_owner(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetThemeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Theme",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.theme)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_theme(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetDescriptionButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set Description",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.description)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_description(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleLockedButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Locked",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_locked(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ToggleDisabledButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Disabled",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_disabled(interaction)
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
class SetIndexButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Index",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_index(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class AddImageButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.success,
            label="Add Image",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_image(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class RemoveImageButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Image",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_image(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
