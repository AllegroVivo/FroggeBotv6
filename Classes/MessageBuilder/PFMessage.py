from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional, Type, TypeVar, List, Dict, Any

from discord import User, Embed, SelectOption, Interaction

from Classes.Common import ManagedObject
from Utilities import Utilities as U
from UI.MessageBuilder import PFMessageBuilderView
from UI.Common import BasicTextModal

if TYPE_CHECKING:
    from Classes import MessageBuilder, SymbolMap, SymbolItem
    from UI.Common import FroggeView
################################################################################

__all__ = ("PFMessage",)

PFM = TypeVar("PFM", bound="PFMessage")

################################################################################
class PFMessage(ManagedObject):

    __slots__ = (
        "_name",
        "_msg",
    )

################################################################################
    def __init__(self, mgr: MessageBuilder, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._name: Optional[str] = kwargs.pop("name")
        self._msg: List[Dict[str, Any]] = kwargs.pop("msg", [])

################################################################################
    @classmethod
    def new(cls: Type[PFM], mgr: MessageBuilder, name: str) -> PFM:

        new_data = mgr.bot.api.create_pf_message(mgr.guild_id, name)
        return cls(mgr, new_data["id"], name=name)

################################################################################
    @classmethod
    def load(cls: Type[PFM], mgr: MessageBuilder, data: Dict[str, Any]) -> PFM:

        return cls(
            mgr=mgr,
            _id=data["id"],
            name=data["name"],
            msg=json.loads(data["message"]) if data["message"] else []
        )

################################################################################
    def __len__(self) -> int:

        return len(self._msg)

################################################################################
    @property
    def name(self) -> Optional[str]:

        return self._name

################################################################################
    @property
    def message(self) -> List[Dict[str, Any]]:

        return self._msg

################################################################################
    @property
    def symbol_set_dict(self) -> Dict[str, SymbolMap]:

        return {s.name: s for s in self._mgr.symbol_sets}  # type: ignore

################################################################################
    @property
    def all_symbols(self) -> List[SymbolItem]:

        return self._mgr.all_symbols  # type: ignore

################################################################################
    def symbol_options(self) -> List[SelectOption]:

        return [SelectOption(label=s.name, value=s.name) for s in self._mgr.symbol_sets]  # type: ignore

################################################################################
    def emoji_string(self) -> str:

        if not self._msg:
            return "** **"

        ret = ""
        for character in self._msg:
            if character["type"] == "symbol":
                symbol = next((s for s in self.all_symbols if s.id == character["value"]), None)
                if symbol:
                    ret += str(symbol.emoji)
            elif character["type"] == "text":
                ret += character["value"]

        return ret

################################################################################
    def message_string(self) -> str:

        if not self._msg:
            return " "

        ret = ""
        for character in self._msg:
            if character["type"] == "symbol":
                symbol = next((s for s in self.all_symbols if s.id == character["value"]), None)
                if symbol:
                    ret += symbol.unicode
            elif character["type"] == "text":
                ret += character["value"]

        return ret

################################################################################
    def update(self) -> None:

        self.bot.api.update_pf_message(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "name": self._name,
            "message": json.dumps(self._msg) if self._msg else None
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_pf_message(self.id)
        self._mgr._managed.remove(self)

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title=f"{self.name or 'Unnamed Message'} Status",
            description=(
                f"```{self.message_string()}```\n"
                f"{self.emoji_string()}"
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return PFMessageBuilderView(user, self)

################################################################################
    def add_symbol(self, symbol: SymbolItem) -> None:

        self._msg.append({
            "type": "symbol",
            "value": symbol.id
        })
        self.update()

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.name or "Unnamed Message",
            value=str(self.id)
        )

################################################################################
    async def add_text(self, interaction: Interaction, text: Optional[str] = None) -> None:

        if text is None:
            modal = BasicTextModal(
                title="Add Plain Text",
                attribute="Text",
                max_length=200 - len(self),
                required=False
            )

            await interaction.response.send_modal(modal)
            await modal.wait()

            if not modal.complete or not modal.value:
                return

            text = modal.value

        self._msg.append({
            "type": "text",
            "value": text
        })
        self.update()

################################################################################
    def backspace(self) -> None:

        self._msg = self._msg[:-1]
        self.update()

################################################################################
