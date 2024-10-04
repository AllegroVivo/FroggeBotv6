from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict

from Classes.Common import Identifiable
from Enums import ElementType

if TYPE_CHECKING:
    from Classes import EventTemplate, EventElement
################################################################################

__all__ = ("TemplateElement",)

TS = TypeVar("TS", bound="TemplateSecondary")

################################################################################
class TemplateElement(Identifiable):

    __slots__ = (
        "_parent",
        "_type",
        "_title",
        "_value",
    )

################################################################################
    def __init__(self, parent: EventTemplate, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: EventTemplate = parent

        self._type: ElementType = kwargs.pop("type")
        self._title: Optional[str] = kwargs.get("title")
        self._value: Optional[str] = kwargs.get("value")

################################################################################
    @classmethod
    def from_event(cls: Type[TS], parent: EventTemplate, secondary: EventElement) -> TS:

        self: TS = cls.__new__(cls)

        self._parent = parent

        self._type = secondary.type
        self._title = secondary.title
        self._value = secondary.value

        new_data = parent.bot.api.create_template_element(self)
        self._id = new_data["id"]

        return self

################################################################################
    @classmethod
    def load(cls: Type[TS], parent: EventTemplate, data: Dict[str, Any]) -> TS:

        return cls(
            parent=parent,
            _id=data["id"],
            type=ElementType(data["element_type"]),
            title=data["title"],
            value=data["value"]
        )

################################################################################
    def to_dict(self) -> dict:

        return {
            "template_id": self._parent.id,
            "element_type": self._type,
            "title": self._title,
            "value": self._value
        }

################################################################################

