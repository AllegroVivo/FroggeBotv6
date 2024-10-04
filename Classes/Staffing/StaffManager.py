from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any, Dict, Tuple

from discord import Embed, Interaction, User, EmbedField, Role, Forbidden, NotFound

from Errors import InsufficientPermissions, RoleMissing
from UI.Common import ConfirmCancelView, FroggeView, BasicTextModal
from UI.Staffing import StaffingMainMenuView, EmployeeManagementMenuView
from Utilities import Utilities as U
from .StaffMember import StaffMember
from Classes.Common import ObjectManager, LazyRole

if TYPE_CHECKING:
    from Classes import GuildData, Character
################################################################################

__all__ = ("StaffManager",)

################################################################################
class StaffManager(ObjectManager):

    __slots__ = (
        "_staff_role",
    )
    
################################################################################
    def __init__(self, guild: GuildData):
        
        super().__init__(guild)
        
        self._staff_role: LazyRole = None  # type: ignore
        
################################################################################
    async def load_all(self, data: Dict[str, Any]):

        self._managed = [StaffMember.load(self, s) for s in data["staff"]]
        self._staff_role = LazyRole(self, data["role_id"])
        
################################################################################
    def __getitem__(self, user_id: int) -> Optional[StaffMember]:

        return next((m for m in self._managed if m._user.id == int(user_id)), None)

################################################################################
    @property
    def staff(self) -> List[StaffMember]:
        
        return self._managed  # type: ignore
    
################################################################################
    @property
    async def staff_role(self) -> Optional[Role]:
        
        return await self._staff_role.get()
    
    @staff_role.setter
    def staff_role(self, role: Role) -> None:
        
        self._staff_role.set(role)
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_staff_manager(self)
        
################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "role_id": self._staff_role.id
        }

################################################################################
    async def status(self) -> Embed:
        
        staff_role = await self.staff_role
        return U.make_embed(
            title="__Staffing Main Menu__",
            description=(
                "Please select an option below to manage various "
                "staffing module elements."
            ),
            fields=[
                EmbedField(
                    name="__Staff Role__",
                    value=(
                        staff_role.mention
                        if staff_role is not None
                        else "`Not Set`"
                    ),
                    inline=True
                )
            ]
        )
    
################################################################################
    def get_character(self, character_id: str) -> Optional[Character]:

        return next((c for s in self.staff for c in s.characters if c.id == character_id), None)
    
################################################################################
    def employee_status(self) -> Embed:
        
        return U.make_embed(
            title="__Employee Management Menu__",
            description=(
                f"**[{len(self._managed)}]** staff members are currently registered."
            ),
        )
    
################################################################################
    async def employee_management_menu(self, interaction: Interaction) -> None:
        
        embed = self.employee_status()
        view = EmployeeManagementMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return StaffingMainMenuView(user, self)

################################################################################
    async def user_menu(self, interaction: Interaction, user: User) -> None:

        member = self[user.id]
        if member is None:
            error = U.make_error(
                title="User Not Registered",
                message=f"{user.mention} is not registered as a staff member.",
                solution="Please hire this user before proceeding."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        await member.menu(interaction)
        
################################################################################
    async def add_item(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Add Employee__",
            description=(
                "Please enter a user mention of the server member "
                "you wish to add as staff."
            ),
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return

        await self.hire(interaction, user)
    
################################################################################
    async def hire(self, interaction: Interaction, user: User) -> None:

        confirm = U.make_embed(
            title="__Confirm Employee Add__",
            description=(
                f"Are you sure you want to add {user.mention} ({user.display_name}) "
                f"as a staff member?"
            ),
        )
        view = ConfirmCancelView(interaction.user, return_interaction=True)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        response, inter = view.value

        staff_role = await self.staff_role
        if staff_role is not None:
            server_member = await self.guild.get_or_fetch_member(user.id)
            try:
                await server_member.add_roles(staff_role)
            except Forbidden:
                error = InsufficientPermissions(None, "Add Roles")
                await interaction.respond(embed=error, ephemeral=True)
            except NotFound:
                error = RoleMissing(staff_role.name)
                await interaction.respond(embed=error, ephemeral=True)

        member = self[user.id]
        if member is not None:
            await member.rehire(interaction)
            return

        modal = BasicTextModal(
            title="Enter Character Name",
            attribute="Character Name",
            example="e.g. 'Allegro Vivo'",
            max_length=40,
        )

        await inter.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        member = StaffMember.new(self, user.id, modal.value)
        self._managed.append(member)

        await member.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Employee__",
            description=(
                "Please enter a user mention of the server member "
                "you wish to modify."
            ),
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return
        
        await self.user_menu(interaction, user)
    
################################################################################
    async def remove_item(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Terminate Employee__",
            description=(
                "Please enter a user mention of the server member "
                "you wish to terminate."
            ),
        )

        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return

        member = self[user.id]
        error = None

        if member is None:
            error = U.make_error(
                title="User Not Registered",
                message=f"{user.mention} is not registered as a staff member.",
                solution="Please hire this user before proceeding."
            )
        elif member.is_terminated:
            error = U.make_error(
                title="Employee Already Terminated",
                message=f"{user.mention} is already terminated.",
                solution="No further action is required."
            )

        if error is not None:
            await interaction.respond(embed=error, ephemeral=True)
            return

        await member.remove(interaction)
    
################################################################################
    async def employee_report(self, interaction: Interaction) -> None:
        
        pass
    
################################################################################
    async def employee_statistics(self, interaction: Interaction) -> None:
        
        pass
    
################################################################################
    async def positions_main_menu(self, interaction: Interaction) -> None:
        
        # This is here because we wanted to reduce the number of slash commands,
        # so we're using a button on a staffing menu instead.
        await self.guild.position_manager.main_menu(interaction)
        
################################################################################
    async def set_staff_role(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Staff Role__",
            description=(
                "Please enter a role mention to set as the staff role."
            ),
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return
        
        self.staff_role = role
        
################################################################################
    def get_by_id(self, staff_id: int) -> Optional[StaffMember]:

        return next((m for m in self._managed if m.id == int(staff_id)), None)

################################################################################
    def can_work_position(self, pos_id: int) -> List[StaffMember]:

        return [
            m
            for m in self.staff
            if self.guild.position_manager[pos_id] in m.qualifications  # type: ignore
        ]

################################################################################

