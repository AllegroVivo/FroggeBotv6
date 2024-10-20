from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord import User, Interaction, SelectOption, ButtonStyle
from discord.ui import Select

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import PFMessage, SymbolItem
################################################################################

__all__ = ("PFMessageBuilderView",)

################################################################################
class PFMessageBuilderView(FroggeView):

    def __init__(self, owner: User, message: PFMessage):
        
        super().__init__(owner, message)
        
        self.symbol_sets = self.ctx.symbol_set_dict
        self._active_symbol_set = next(iter(self.symbol_sets.values()))

        self.redraw()
        
################################################################################
    def redraw(self) -> None:

        self.clear_items()

        for symbol in self._active_symbol_set.items:
            self.add_item(SymbolButton(symbol))

        # Add Misc Buttons
        self.add_item(EnterPlainTextButton())
        self.add_item(AddSpaceButton())
        self.add_item(BackspaceButton())

        # Add Navigation Select
        self.add_item(SymbolSelect(self.ctx.symbol_options()))

        self.set_button_attributes()

################################################################################
class SymbolButton(FroggeButton):
    
    def __init__(self, symbol: SymbolItem):

        super().__init__(
            label=".",
            row=symbol.button_row
        )

        self.symbol: SymbolItem = symbol

    def set_attributes(self) -> None:
        if self.symbol.emoji == "":
            self.label = self.symbol.name
        else:
            self.emoji = self.symbol.emoji
        
    async def callback(self, interaction: Interaction):
        self.view.ctx.add_symbol(self.symbol)
        await interaction.response.edit_message(embed=await self.view.ctx.status())

################################################################################
class EnterPlainTextButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.primary,
            label="Add Plain Text",
            disabled=False,
            row=3,
            emoji=BotEmojis.Text
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_text(interaction)
        await self.view.edit_message_helper(
            interaction, embed=await self.view.ctx.status(), view=self.view
        )

################################################################################
class AddSpaceButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.success,
            label="Add a Space",
            disabled=False,
            row=3,
            emoji=BotEmojis.Paper
        )

    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_text(interaction, text=" ")

        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=await self.view.ctx.status())
        else:
            await self.view.edit_message_helper(
                interaction, embed=await self.view.ctx.status(), view=self.view
            )

################################################################################
class BackspaceButton(FroggeButton):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.danger,
            label="Backspace",
            disabled=False,
            row=3,
            emoji=BotEmojis.ArrowLeft
        )

    async def callback(self, interaction: Interaction):
        self.view.ctx.backspace()
        await interaction.response.edit_message(embed=await self.view.ctx.status())

################################################################################
class SymbolSelect(Select):

    def __init__(self, options: List[SelectOption]):

        super().__init__(
            placeholder="Select a Symbol Set",
            options=options,
            row=4
        )

    async def callback(self, interaction: Interaction):
        self.view._active_symbol_set = self.view.symbol_sets[self.values[0]]
        self.view.redraw()

        await interaction.response.edit_message(embed=await self.view.ctx.status(), view=self.view)

################################################################################
