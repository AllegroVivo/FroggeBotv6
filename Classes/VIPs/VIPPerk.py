from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict

from Enums import Repeatability
from discord import Embed, Interaction, SelectOption
from Utilities import Utilities as U
from UI.VIPs import VIPPerkStatusView
from UI.Common import BasicTextModal, FroggeSelectView

if TYPE_CHECKING:
    from Classes import VIPPerksManager
################################################################################

__all__ = ("VIPPerk", )

VP = TypeVar("VP", bound="VIPPerk")

################################################################################
class VIPPerk:

    __slots__ = (
        "_id",
        "_mgr",
        "_text",
        "_description",
        "_repeatability",
    )
    
################################################################################
    def __init__(self, mgr: VIPPerksManager, _id: int, **kwargs) -> None:

        self._id: int = _id
        self._mgr: VIPPerksManager = mgr
        
        self._text: Optional[str] = kwargs.get("text")
        self._description: Optional[str] = kwargs.get("description")
        self._repeatability: Repeatability = kwargs.get("repeatability", Repeatability.Monthly)        
    
################################################################################
    @classmethod
    def new(cls: Type[VP], mgr: VIPPerksManager) -> VP:
        
        new_perk = mgr.bot.api.create_vip_perk(mgr.guild.guild_id, mgr._parent.id)
        return cls(mgr=mgr, _id=new_perk["id"])
    
################################################################################
    @classmethod
    def load(cls: Type[VP], mgr: VIPPerksManager, data: Dict[str, Any]) -> VP:
        
        return cls(
            mgr=mgr,
            _id=data["id"],
            text=data["text_value"],
            description=data["description"],
            repeatability=Repeatability(data["repeatability"])
        )
    
################################################################################
    def __eq__(self, other: VIPPerk) -> bool:
        
        return self.id == other.id
    
################################################################################
    @property
    def id(self) -> int:
        
        return self._id
    
################################################################################
    @property
    def text(self) -> Optional[str]:
        
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        
        self._text = value
        self.update()
        
################################################################################
    @property
    def description(self) -> Optional[str]:
        
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        
        self._description = value
        self.update()
        
################################################################################
    @property
    def repeatability(self) -> Repeatability:
        
        return self._repeatability
    
    @repeatability.setter
    def repeatability(self, value: Repeatability) -> None:
        
        self._repeatability = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self._mgr.bot.api.update_vip_perk(self)
        
################################################################################
    def delete(self) -> None:
        
        self._mgr.bot.api.delete_vip_perk(self)
        self._mgr.perks.remove(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "text_value": self.text,
            "description": self.description,
            "repeatability": self.repeatability.value
        }
    
################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title=f"Perk: `{self.text or 'No Name'}`",
            description=(
                f"**Repeatability:** {self.repeatability.proper_name}\n\n"

                f"**Description:**\n"
                f"{self.description}"
            )
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = VIPPerkStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self.text,
            value=str(self.id),
            description=(
                self.description
                if len(self.description) <= 50
                else f"{self.description[:47]}..."
            ) if self.description else None
        )

################################################################################
    async def set_text(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="VIP Perk Text",
            attribute="Text",
            cur_val=self.text,
            example="e.g. '3 Free Photoshoots'",
            max_length=80,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.text = modal.value

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="VIP Perk Description",
            attribute="Description",
            cur_val=self.description,
            max_length=150,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value

################################################################################
    async def set_repeatability(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Repeatability",
            description="Please select the repeatability for this VIP Perk."
        )
        view = FroggeSelectView(interaction.user, Repeatability.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.repeatability = Repeatability(int(view.value))

################################################################################

