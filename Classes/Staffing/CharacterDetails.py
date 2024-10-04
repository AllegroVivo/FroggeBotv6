from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Any, Tuple

if TYPE_CHECKING:
    from Classes import Character
################################################################################

__all__ = ("CharacterDetails",)

CD = TypeVar("CD", bound="CharacterDetails")

################################################################################
class CharacterDetails:

    __slots__ = (
        "_parent",
        "_name",
    )

################################################################################
    def __init__(self, parent: Character, **kwargs):

        self._parent: Character = parent

        self._name: str = kwargs.get("name")

################################################################################
    @classmethod
    def load(cls: Type[CD], parent: Character, data: Tuple[Any, ...]) -> CD:

        self: CD = cls.__new__(cls)

        self._parent = parent
        self._name = data[2]

        return self

################################################################################
    @property
    def name(self) -> str:

        return self._name

################################################################################
