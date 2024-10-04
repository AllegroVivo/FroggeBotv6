from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, TypeVar, Any, Dict
from discord import Embed, EmbedField, Interaction, Forbidden, NotFound

from Errors import InsufficientPermissions, RoleMissing
from UI.Common import FroggeSelectView
from Utilities import Utilities as U
from UI.Staffing import StaffQualificationMenuView

if TYPE_CHECKING:
    from Classes import StaffMember, Position
################################################################################

__all__ = ("StaffQualifications", )

SQ = TypeVar("SQ", bound="StaffQualifications")

################################################################################
class StaffQualifications:

    __slots__ = (
        "_parent",
        "_qualifications",
    )

################################################################################
    def __init__(self, parent: StaffMember, **kwargs) -> None:

        self._parent: StaffMember = parent
        self._qualifications: List[Position] = kwargs.get("qualifications", [])

################################################################################
    @classmethod
    def load(cls: Type[SQ], parent: StaffMember, data: List[int]) -> SQ:

        self: SQ = cls.__new__(cls)

        self._parent = parent
        self._qualifications = [parent.guild.position_manager[p] for p in data]

        return self

################################################################################
    def __contains__(self, item: Position) -> bool:

        return item in self._qualifications

################################################################################
    @property
    def positions(self) -> List[Position]:

        return self._qualifications

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title=f"__`{self._parent._details.name}'s` Qualifications__",
            fields=[
                EmbedField(
                    name="Positions",
                    value="\n".join([f"* `{p.name}`" for p in self.positions]) or "`None`",
                    inline=False
                )
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = StaffQualificationMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_qualifications(self, interaction: Interaction) -> None:

        all_positions = self._parent.manager.guild.position_manager.select_options()
        position_opts = [
            p
            for p in all_positions
            if p.value not in [p.id for p in self.positions]
        ]

        prompt = U.make_embed(
            title="__Add Qualifications__",
            description=(
                "Please select the name of the position(s) you would like to add "
                "to this staff member."
            )
        )
        view = FroggeSelectView(interaction.user, position_opts, multi_select=True)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        positions = [self._parent.manager.guild.position_manager[p] for p in view.value]

        self._qualifications.extend(positions)  # type: ignore
        self._parent.update()

        server_member = await self._parent.guild.get_or_fetch_member(self._parent._user.id)
        for pos in positions:
            role = await pos.role  # type: ignore
            if role is None:
                continue
            try:
                await server_member.add_roles(role)
            except Forbidden:
                error = InsufficientPermissions(None, "Add Roles")
                await interaction.respond(embed=error, ephemeral=True)
            except NotFound:
                error = RoleMissing(role.name)
                await interaction.respond(embed=error, ephemeral=True)

################################################################################
    async def remove_qualifications(self, interaction: Interaction) -> None:

        all_positions = self._parent.manager.guild.position_manager.select_options()
        position_opts = [
            p
            for p in all_positions
            if int(p.value) in [p.id for p in self.positions]
        ]

        prompt = U.make_embed(
            title="__Remove Qualifications__",
            description=(
                "Please select the name of the position(s) you would like to remove "
                "from this staff member."
            )
        )
        view = FroggeSelectView(interaction.user, position_opts, multi_select=True)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        positions = [self._parent.manager.guild.position_manager[p] for p in view.value]

        server_member = await self._parent.guild.get_or_fetch_member(self._parent._user.id)
        for pos in positions:
            role = await pos.role  # type: ignore
            if role is None:
                continue
            try:
                await server_member.remove_roles(role)
            except Forbidden:
                error = InsufficientPermissions(None, "Remove Roles")
                await interaction.respond(embed=error, ephemeral=True)
            except NotFound:
                error = RoleMissing(role.name)
                await interaction.respond(embed=error, ephemeral=True)

        for p in positions:
            if p in self._qualifications:
                self._qualifications.remove(p)  # type: ignore
        self._parent.update()

################################################################################

