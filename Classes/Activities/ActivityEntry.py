from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, TypeVar, Any, Tuple

from discord import User

from Classes.Common import Identifiable, LazyUser

if TYPE_CHECKING:
    from Classes import BaseActivity, FroggeBot, GuildData
################################################################################

__all__ = ("ActivityEntry", )

T = TypeVar("T")

################################################################################
class ActivityEntry(Identifiable, ABC):

    __slots__ = (
        "_parent",
        "_user",
        "_qty",
    )
    
################################################################################
    def __init__(self, parent: BaseActivity, _id: int, user_id: int, qty: int) -> None:

        super().__init__(_id)

        self._parent: BaseActivity = parent
        self._user: LazyUser = LazyUser(self, user_id)
        self._qty: int = qty
    
################################################################################
    @classmethod
    @abstractmethod
    def load(cls: Type[T], parent: BaseActivity, data: Tuple[Any, ...]) -> T:
        
        raise NotImplementedError
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:

        return self._parent.guild

################################################################################
    @property
    def id(self) -> int:

        return self._id

################################################################################
    @property
    async def user(self) -> User:
        
        return await self._user.get()
    
################################################################################
    @property
    def quantity(self) -> int:
        
        return self._qty
    
    @quantity.setter
    def quantity(self, qty: int) -> None:
        
        self._qty = qty
        self.update()
        
################################################################################
    @abstractmethod
    def update(self) -> None:
        
        raise NotImplementedError
    
################################################################################
    @abstractmethod
    def delete(self) -> None:
        
        raise NotImplementedError
    
################################################################################
    @abstractmethod
    async def notify(self) -> bool:
        
        raise NotImplementedError
    
################################################################################
    