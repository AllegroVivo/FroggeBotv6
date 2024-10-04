from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, TypeVar, Generic, Optional, Union, Any

from discord import Message, Role, User, Member
from discord.abc import GuildChannel

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################

__all__ = (
    "LazyRole",
    "LazyUser",
    "LazyChannel",
    "LazyMessage",
)

T = TypeVar("T")

################################################################################
class LazyLoadableType(Enum):
    
    Role = 1
    User = 2
    Channel = 3
    Message = 4
    
################################################################################
class LazyLoadable(Generic[T]):

    __slots__ = (
        "_parent",
        "_item_type",
        "_item_id",
        "_item"
    )
    
################################################################################
    def __init__(self, parent: Any, _type: LazyLoadableType, item_id: Optional[int]) -> None:

        self._parent: Any = parent
        self._item_type: LazyLoadableType = _type
        
        self._item_id: Optional[Union[int, str]] = item_id
        self._item: Optional[T] = None
    
################################################################################
    def __eq__(self, other: LazyLoadable) -> bool:

        return self._item_id == other._item_id

################################################################################
    @property
    def id(self) -> Optional[Union[int, str]]:
        
        return self._item_id
    
################################################################################
    @property
    def name(self) -> Optional[str]:
        
        return self._item.name if self._item is not None else "Unloaded Loadable"
    
################################################################################
    async def get(self) -> Optional[T]:

        guild = getattr(self._parent, "guild", None)
        assert guild is not None

        if self._item is None and self._item_id is not None:
            self._item = await self._fetch_item(guild)
        return self._item
    
################################################################################
    async def _fetch_item(self, guild: GuildData) -> T:
        
        match self._item_type:
            case LazyLoadableType.Role:
                action = guild.get_or_fetch_role
            case LazyLoadableType.User:
                action = guild.get_or_fetch_member_or_user
            case LazyLoadableType.Channel:
                action = guild.get_or_fetch_channel
            case LazyLoadableType.Message:
                action = guild.get_or_fetch_message
            case _:
                raise NotImplementedError(f"LazyLoadableType: {self._item_type} not implemented")

        return await action(self._item_id)
    
################################################################################
    def set(self, item: T) -> None:

        if item is None:
            self._item_id = None
        elif isinstance(item, Message):
            self._item_id = item.jump_url
        else:
            assert isinstance(item, (Role, GuildChannel, User, Member))
            self._item_id = item.id
        
        self._item = item
        
        if getattr(self._parent, "update", None) is not None:
            self._parent.update()
        
################################################################################
class LazyRole(LazyLoadable):

    def __init__(self, parent: Any, role_id: Optional[int]) -> None:
        super().__init__(parent, LazyLoadableType.Role, role_id)
        
################################################################################
class LazyUser(LazyLoadable):

    def __init__(self, parent: Any, user_id: Optional[int]) -> None:
        super().__init__(parent, LazyLoadableType.User, user_id)
        
################################################################################
class LazyChannel(LazyLoadable):

    def __init__(self, parent: Any, channel_id: Optional[int]) -> None:
        super().__init__(parent, LazyLoadableType.Channel, channel_id)
        
################################################################################
class LazyMessage(LazyLoadable):

    def __init__(self, parent: Any, jump_url: Optional[str]) -> None:
        super().__init__(parent, LazyLoadableType.Message, jump_url)
        
################################################################################
