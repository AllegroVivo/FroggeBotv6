from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Dict, Any

from discord import (
    SelectOption,
    User,
    Embed,
    EmbedField,
    Role,
    Interaction,
    Member,
    Forbidden
)

from Classes.Common import ManagedObject, LazyRole
from Classes.Common.FroggeObject import T
from Errors import InsufficientPermissions
from UI.Common import ConfirmCancelView, BasicTextModal
from UI.Verification import RoleRelationStatusView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import VerificationManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("VerificationRoleRelation", )

RR = TypeVar("RR", bound="VerificationRoleRelation")

################################################################################
class VerificationRoleRelation(ManagedObject):

    __slots__ = (
        "_pending",
        "_final",
        "_message",
    )
    
################################################################################
    def __init__(self, mgr: VerificationManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)
        
        self._pending: LazyRole = LazyRole(self, kwargs.get("pending_role_id"))
        self._final: LazyRole = LazyRole(self, kwargs.get("final_role_id"))
        self._message: Optional[str] = kwargs.get("message")
    
################################################################################
    @classmethod
    def new(cls: Type[RR], mgr: VerificationManager) -> RR:
        
        new_data = mgr.bot.api.create_role_relation(mgr.guild_id)
        return cls(mgr, new_data["id"])
    
################################################################################
    @classmethod
    async def load(cls: Type[T], mgr: VerificationManager, data: Dict[str, Any]) -> T:
        
        return cls(mgr, data["id"], **data)
    
################################################################################
    @property
    async def pending_role(self) -> Role:

        return await self._pending.get()
    
    @pending_role.setter
    def pending_role(self, role: Role) -> None:
        
        self._pending.set(role)
        
################################################################################
    @property
    async def final_role(self) -> Role:

        return await self._final.get()
    
    @final_role.setter
    def final_role(self, role: Role) -> None:
        
        self._final.set(role)
        
################################################################################
    @property
    def message(self) -> Optional[str]:

        return self._message
    
    @message.setter
    def message(self, value: Optional[str]) -> None:
        
        self._message = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_role_relation(self)
    
################################################################################
    def delete(self) -> None:
        
        self.bot.api.delete_role_relation(self)
        self._mgr._relations.remove(self)  # type: ignore
    
################################################################################
    def to_dict(self) -> Dict[str, Any]:
            
        return {
            "pending_role_id": self._pending.id,
            "final_role_id": self._final.id,
            "message": self.message
        }
    
################################################################################
    async def status(self) -> Embed:
        
        pending_role = await self.pending_role
        pending_value = (
            pending_role.mention
            if pending_role is not None
            else "`Not Set`"
        )
        
        final_role = await self.final_role
        final_value = (
            final_role.mention
            if final_role is not None
            else "`Not Set`"
        )

        return U.make_embed(
            title="__Role Relation Status__",
            description=(
                "__**Welcome Message**__\n"
                f"{self.message or '`Not Set`'}"
            ),
            fields=[
                EmbedField(
                    name="__Pending Role__",
                    value=(
                        f"{pending_value}\n"
                        "*(Role that the user will\n"
                        "have prior to verification)*"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Final Role__",
                    value=(
                        f"{final_value}\n"
                        "*(Role that the user will\n"
                        "be given after verification)*"
                    ),
                    inline=True
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return RoleRelationStatusView(user, self)
    
################################################################################
    async def set_pending(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Pending Role__",
            description=(
                "Please mention the role that you would like to set as the pending role.\n"
                "*(Role that the user will have prior to verification)*"
            )
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self.pending_role = role

################################################################################
    async def set_final(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Future Role__",
            description=(
                "Please mention the role that you would like to set as the future role.\n"
                "*(Role that the user will be given after successful verification)*"
            )
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self.final_role = role

################################################################################
    async def select_option(self) -> SelectOption:

        pending_role = await self.pending_role
        pending_value = (
            pending_role.name
            if pending_role is not None
            else "Pending Not Set"
        )
        
        final_role = await self.final_role
        final_value = (
            final_role.name
            if final_role is not None
            else "Final Not Set"
        )

        return SelectOption(
            label=U.string_clamp(f"{pending_value} -> {final_value}", 95),
            value=str(self.id)
        )

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Role Relation__",
            description=(
                "Are you sure you want to remove this role relation?\n"
                "*(This action cannot be undone)*"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
    async def check_swap(self, interaction: Interaction, member: Member) -> Optional[str]:

        pending_role = await self.pending_role
        final_role = await self.final_role
        
        if pending_role is None or final_role is None:
            return

        if pending_role not in member.roles:
            return

        try:
            await member.remove_roles(pending_role)
            await member.add_roles(final_role)
        except Forbidden:
            error = InsufficientPermissions(None, "Manage Roles")
            await interaction.respond(embed=error, ephemeral=True)
        else:
            return self.message

################################################################################
    async def set_message(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Welcome Message Text",
            attribute="Text",
            cur_val=self.message,
            max_length=2000,
            required=False,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.message = modal.value

################################################################################
