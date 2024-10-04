from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, TypeVar, Type, Tuple, Any

from discord import Interaction

from UI.Common import BasicTextModal, BasicNumberModal

if TYPE_CHECKING:
    from Classes import BaseActivity, FroggeBot
################################################################################

__all__ = ("ActivityDetails", )

T = TypeVar("T")

################################################################################
class ActivityDetails(ABC):

    __slots__ = (
        "_parent",
        "_name",
        "_prize",
        "_num_winners",
        "_auto_notify",
    )
    
################################################################################
    def __init__(self, parent: BaseActivity, **kwargs) -> None:

        self._parent: BaseActivity = parent
        
        self._name: Optional[str] = kwargs.get("name")
        self._prize: Optional[str] = kwargs.get("prize")
        self._num_winners: int = kwargs.get("num_winners", 1)
        self._auto_notify: bool = kwargs.get("auto_notify", True)
    
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
    def parent_id(self) -> int:
        
        return self._parent.id
    
################################################################################
    @property
    def name(self) -> Optional[str]:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
        
################################################################################
    @property
    def prize(self) -> Optional[str]:
        
        return self._prize
    
    @prize.setter
    def prize(self, value: str) -> None:
        
        self._prize = value
        self.update()
        
################################################################################
    @property
    def num_winners(self) -> int:
        
        return self._num_winners
    
    @num_winners.setter
    def num_winners(self, value: int) -> None:
        
        self._num_winners = value
        self.update()
        
################################################################################
    @property
    def auto_notify(self) -> bool:
        
        return self._auto_notify
    
    @auto_notify.setter
    def auto_notify(self, value: bool) -> None:
        
        self._auto_notify = value
        self.update()
        
################################################################################
    @abstractmethod
    def update(self) -> None:
        
        raise NotImplementedError
    
################################################################################
    async def set_name(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title=f"Set {self._parent.activity_name} Name",
            attribute="Name",
            cur_val=self.name,
            example="eg. 'Dawntrail Giveaway'",
            max_length=80
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.name = modal.value
    
################################################################################
    async def set_prize(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title=f"Set {self._parent.activity_name} Prize",
            attribute="Prize",
            cur_val=self.prize,
            example="eg. '1 Million Frogs'",
            max_length=50
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.prize = modal.value
    
################################################################################
    async def set_num_winners(self, interaction: Interaction) -> None:

        modal = BasicNumberModal(
            title=f"Set {self._parent.activity_name} Number of Winners",
            attribute="Num. Winners",
            cur_val=self.num_winners,
            example="eg. '3'",
            max_length=1
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.num_winners = modal.value
    
################################################################################
    async def toggle_auto_notify(self, interaction: Interaction) -> None:
        
        self.auto_notify = not self.auto_notify
        await interaction.respond("** **", delete_after=0.1)
    
################################################################################
    