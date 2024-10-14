from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from discord import Interaction, User, Embed
from dotenv import load_dotenv

from Classes.Common import ObjectManager
from Utilities import Utilities as U
from .SymbolMap import SymbolMap
from .PFMessage import PFMessage
from UI.MessageBuilder import MessageBuilderMenuView
from Errors import MaxItemsReached
from UI.Common import BasicTextModal, FroggeSelectView

if TYPE_CHECKING:
    from Classes import GuildData, SymbolItem
    from UI.Common import FroggeView
################################################################################

__all__ = ("MessageBuilder", )

################################################################################
class MessageBuilder(ObjectManager):

    __slots__ = (
        "_symbols",
    )

    MAX_MESSAGES = 80

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

        self._symbols: List[SymbolMap] = []

        load_dotenv()
        subfolder = "Dev" if os.getenv("DEBUG") == "True" else "Prod"

        for json_file in Path(f"Classes/MessageBuilder/Maps/{subfolder}").glob('*.json'):
            with json_file.open('r', encoding='utf-8') as file:
                self._symbols.append(SymbolMap(json.load(file)))

################################################################################
    async def load_all(self, payload: List[Dict[str, Any]]) -> None:

        self._managed = [PFMessage.load(self, data) for data in payload]

################################################################################
    @property
    def messages(self) -> List[PFMessage]:

        return self._managed  # type: ignore

################################################################################
    @property
    def all_symbols(self) -> List[SymbolItem]:

        return [symbol for symbol_set in self._symbols for symbol in symbol_set.items]

################################################################################
    @property
    def symbol_sets(self) -> List[SymbolMap]:

        return self._symbols

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title="__Message Builder Main Menu__",
            description=(
                f"**[`{len(self)}/80`]** messages saved.\n\n"
                
                "Select an option below to continue."
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return MessageBuilderMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self.messages) >= self.MAX_MESSAGES:
            error = MaxItemsReached("PF Message", self.MAX_MESSAGES)
            await interaction.respond(embed=error, ephemeral=True)
            return

        modal = BasicTextModal(
            title="Enter Message Name",
            attribute="Name",
            example="eg. 'Pre-Open PF Message'",
            max_length=50,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        new_message = PFMessage.new(self, modal.value)
        self._managed.append(new_message)

        await new_message.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Embed__",
            description=(
                "Please select a message to modify."
            )
        )
        view = FroggeSelectView(interaction.user, [e.select_option() for e in self.messages])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        message = self[view.value]
        await message.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Embed__",
            description=(
                "Please select a message to modify."
            )
        )
        view = FroggeSelectView(interaction.user, [e.select_option() for e in self.messages])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        message = self[view.value]
        await message.remove(interaction)

################################################################################
