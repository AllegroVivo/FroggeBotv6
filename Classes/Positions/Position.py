from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, TypeVar, Type

from discord import User, Embed, EmbedField, SelectOption, Interaction, Role

from Classes.Common import ManagedObject, LazyRole
from UI.Common import FroggeView, BasicTextModal
from UI.Positions import PositionStatusView
from Utilities import Utilities as U
from logger import log
from Errors import InvalidMonetaryAmount

if TYPE_CHECKING:
    from Classes import PositionManager
################################################################################

__all__ = ("Position", )

P = TypeVar("P", bound="Position")

################################################################################
class Position(ManagedObject):

    __slots__ = (
        "_name",
        "_role",
        "_salary",
    )
    
################################################################################
    def __init__(self, mgr: PositionManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._name: Optional[str] = kwargs.get("name")
        self._role: Optional[LazyRole] = LazyRole(self, kwargs.get("role_id"))
        self._salary: Optional[int] = kwargs.get("salary")
    
################################################################################
    @classmethod
    def new(cls: Type[P], mgr: PositionManager, **kwargs) -> P:

        new_position = mgr.bot.api.create_position(mgr.guild_id)
        return cls(
            mgr=mgr, 
            _id=new_position["id"],
            name=new_position["name"],
            role_id=new_position["role_id"],
            salary=new_position["salary"]
        )

################################################################################
    @classmethod
    def from_dict(cls: Type[P], data: Dict[str, Any], **kwargs) -> P:

        return cls(
            mgr=kwargs["mgr"],
            _id=data["id"],
            name=data["name"],
            role_id=data["role_id"],
            salary=data["salary"]
        )

################################################################################
    def update(self) -> None:

        self._mgr.bot.api.update_position(self)

################################################################################
    def delete(self) -> None:

        self._mgr.bot.api.delete_position(self)
        self._mgr.positions.remove(self)  # type: ignore

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self._id,
            "name": self._name,
            "role_id": self._role.id,
            "salary": self._salary
        }

################################################################################
    @property
    def id(self) -> int:
        
        return self._id
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
        
################################################################################
    @property
    async def role(self) -> Optional[Role]:
        
        return await self._role.get()
    
    @role.setter
    def role(self, value: Role) -> None:

        self._role.set(value)
        
################################################################################
    @property
    def salary(self) -> int:
        
        return self._salary
    
    @salary.setter
    def salary(self, value: int) -> None:
        
        self._salary = value
        self.update()
        
################################################################################
    async def status(self) -> Embed:

        role = await self.role
        return U.make_embed(
            title=f"Position Status: __{self.name}__",
            fields=[
                EmbedField(
                    name="__Linked Role__",
                    value=role.mention if role is not None else "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Salary__",
                    value=(
                        f"`{self.salary:,} gil/hr.`"
                        if self.salary is not None
                        else "`Not Set`"
                    ),
                    inline=True
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return PositionStatusView(user, self)
    
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.name or "Unnamed Position",
            value=str(self.id)
        )
    
################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting name for Position: {self.name}.")

        modal = BasicTextModal(
            title="Position Name",
            attribute="Name",
            cur_val=self.name,
            example="e.g. 'Dancer' or 'Security'",
            max_length=50,
            required=True,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Name change cancelled.")
            return

        self.name = modal.value

        log.info(self.guild, f"Position name changed to: {self.name}.")
        
################################################################################
    async def set_salary(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting salary for Position: {self.name}.")

        modal = BasicTextModal(
            title="Position Salary",
            attribute="Salary per Hour",
            cur_val=f"{self.salary:,}" if self.salary else None,
            example="e.g. '500k' or '1.2m'",
            max_length=11,
            required=False,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            log.debug(self.guild, "Salary change cancelled.")
            return

        raw_salary = modal.value

        log.info(self.guild, f"Attempting to parse salary: {raw_salary}.")

        parsed = U.parse_salary(raw_salary)
        if parsed is None:
            log.warning(self.guild, f"Invalid salary: {raw_salary}.")
            error = InvalidMonetaryAmount(raw_salary)
            await interaction.respond(embed=error, ephemeral=True)
            return

        self.salary = parsed

        log.info(self.guild, f"Position salary changed to: {self.salary:,}.")

################################################################################
    async def set_role(self, interaction: Interaction) -> None:

        log.info(self.guild, f"Setting role for Position: {self.name}.")

        prompt = U.make_embed(
            title="Set Position Role",
            description=(
                "Please mention the role you would like to link to this position."
            )
        )

        if role := await U.listen_for(interaction, prompt, U.MentionableType.Role):
            self.role = role
            log.info(self.guild, f"Position role changed to: {role.name}.")

################################################################################
