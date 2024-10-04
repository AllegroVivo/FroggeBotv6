from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Event
################################################################################

__all__ = ("EventStatusView",)

################################################################################
class EventStatusView(FroggeView):

    def __init__(self, owner: User, event: Event):
        
        super().__init__(owner, event)
        
        button_list = [
            SetNameButton(),
            SetStartTimeButton(),
            SetEndTimeButton(),
            SetImageButton(),
            EditShiftBracketsButton(),
            SelectPositionsButton(),
            AddSecondaryElementButton(),
            PostEventButton(),
            MakeTemplateButton(),
            EditStaffButton(),
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
class SetStartTimeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Start Time",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.start_time)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_start_time(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetEndTimeButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set End Time",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.end_time)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_end_time(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class EditShiftBracketsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Shift Brackets",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.shift_bracket_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SelectPositionsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Edit Positions",
            disabled=False,
            row=1
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.positions)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.positions_menu(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetImageButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Set Image",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.image)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_image(interaction)
        self.set_attributes()
        
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class AddSecondaryElementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Add/Modify Event Elements",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.secondary_element_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class MakeTemplateButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.secondary,
            label="Make Into Template",
            disabled=False,
            row=2,
            emoji=BotEmojis.Star
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.make_template(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PostEventButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Post Event",
            disabled=False,
            row=2,
            emoji=BotEmojis.FlyingEnvelope
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.post(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )
        
################################################################################
class EditStaffButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.secondary,
            label="Manually Edit Staff",
            disabled=False,
            row=2,
            emoji=BotEmojis.Silhouette
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.manual_staff_edit(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
