from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List

from discord import SelectOption

from Enums import ReactionRoleMessageType

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("ReactionRoleTemplate", )

################################################################################
@dataclass
class TemplateRole:

    name: str
    color: str
    emoji: str

################################################################################
class ReactionRoleTemplate:

    __slots__ = (
        "name",
        "title",
        "description",
        "type",
        "thumbnail",
        "roles",
    )

################################################################################
    def __init__(self, data: Dict[str, Any]) -> None:

        self.name: str = data["name"]
        self.title: str = data["title"]
        self.description: str = data["description"]
        self.type: ReactionRoleMessageType = ReactionRoleMessageType(data["type"])
        self.thumbnail: str = data["thumbnail"]
        self.roles: List[TemplateRole] = [TemplateRole(**r) for r in data["roles"]]

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.name,
            value=self.name,
        )

################################################################################
