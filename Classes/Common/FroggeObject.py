from __future__ import annotations

from typing import TypeVar, Type, Any, Dict
################################################################################

__all__ = ("FroggeObject", )

T = TypeVar("T")

################################################################################
class FroggeObject:

    @classmethod
    def new(cls: Type[T], **kwargs) -> T:

        raise NotImplementedError(f"{cls.__name__} objects may not be created directly.")

################################################################################
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any], **kwargs) -> T:

        raise NotImplementedError
    
################################################################################
    def update(self) -> None:

        raise NotImplementedError(f"{self.__class__.__name__} objects may not be updated directly.")
    
################################################################################
    def delete(self) -> None:

        raise NotImplementedError(f"{self.__class__.__name__} objects may not be deleted directly.")
    
################################################################################
    def to_dict(self) -> Dict[str, Any]:

        raise NotImplementedError

################################################################################
