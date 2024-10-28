from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import FroggeEmbed
################################################################################

__all__ = ("EmbedStatusView",)

################################################################################
class EmbedStatusView(FroggeView):

    def __init__(self, owner: User, embed: FroggeEmbed):
        
        super().__init__(owner, embed)
        
        button_list = [
            SetTitleButton(),
            SetDescriptionButton(),
            SetColorButton(),
            SetURLButton(),
            SetTimestampButton(),
            SetHeaderButton(),
            SetFooterButton(),
            SetImagesButton(),
            AddFieldButton(),
            ModifyFieldButton(),
            RemoveFieldButton(),
            CloseMessageButton(),
            PostEmbedButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class SetTitleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            label="Set Title",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.title)
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_title(interaction)
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
class SetColorButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set Color",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.color)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_color(interaction)
        self.set_attributes()

        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetURLButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set URL",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.url)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_url(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetTimestampButton(FroggeButton):

    def __init__(self):

        super().__init__(
            label="Set Timestamp",
            disabled=False,
            row=0
        )

    def set_attributes(self) -> None:
        self.set_style(self.view.ctx.timestamp)

    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_timestamp(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetHeaderButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Header",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.header_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetFooterButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Footer",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.footer_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class SetImagesButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Set Images",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.images_menu(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class AddFieldButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.success,
            label="Add Field",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_field(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class ModifyFieldButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Field",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_field(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class RemoveFieldButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Field",
            disabled=False,
            row=2
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_field(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class PostEmbedButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Post Embed",
            disabled=False,
            row=4,
            emoji=BotEmojis.CheckGreen
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.post(interaction)

################################################################################
