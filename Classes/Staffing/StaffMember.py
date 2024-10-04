from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict, Type, TypeVar, Optional

from discord import Embed, User, EmbedField, Interaction, SelectOption

from Assets import BotEmojis
from Classes.Common import ManagedObject, LazyUser
from UI.Common import FroggeSelectView, ConfirmCancelView, BasicTextModal
from UI.Staffing import StaffMemberMenuView, StaffProfilesMainMenuView
from Utilities import Utilities as U
from .StaffCharacter import StaffCharacter
from .StaffConfiguration import StaffConfiguration
from .StaffDetails import StaffDetails
from .StaffQualifications import StaffQualifications
from .EmploymentPeriod import EmploymentPeriod

if TYPE_CHECKING:
    from Classes import StaffManager, Position, Profile
    from UI.Common import FroggeView
################################################################################

__all__ = ("StaffMember", )

SM = TypeVar("SM", bound="StaffMember")

################################################################################
class StaffMember(ManagedObject):

    __slots__ = (
        "_user",
        "_details",
        "_qualifications",
        "_characters",
        "_config",
    )

################################################################################
    def __init__(self, mgr: StaffManager, _id: int, user_id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._user: LazyUser = LazyUser(self, user_id)
        self._config: StaffConfiguration = kwargs.get("config") or StaffConfiguration(self)

        self._details: StaffDetails = kwargs.get("details") or StaffDetails(self)
        self._qualifications: StaffQualifications = kwargs.get("qualifications") or StaffQualifications(self)
        self._characters: List[StaffCharacter] = kwargs.get("characters", [])

################################################################################
    @classmethod
    def new(cls: Type[SM], mgr: StaffManager, user_id: int, name: str) -> SM:

        data = mgr.bot.api.create_staff_member(mgr.guild_id, user_id, name)

        self: Type[SM] = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._user = LazyUser(self, user_id)
        self._config = StaffConfiguration(self)

        self._details = StaffDetails(self, name=name)
        self._qualifications = StaffQualifications(self)
        self._characters = [StaffCharacter.new(self, name)]

        return self

################################################################################
    @classmethod
    def load(cls: Type[SM], mgr: StaffManager, data: Dict[str, Any]) -> SM:

        self: SM = cls.__new__(cls)

        self._id = data["id"]
        self._mgr = mgr

        self._user = LazyUser(self, data["user_id"])
        self._config = StaffConfiguration.load(self, data["config"])

        self._details = StaffDetails.load(self, data["details"], data["employment_dates"])
        self._qualifications = StaffQualifications.load(self, data["positions"])
        self._characters = [StaffCharacter.load(self, c) for c in data["characters"]]

        return self

################################################################################
    @property
    async def user(self) -> User:

        return await self._user.get()

################################################################################
    @property
    def is_terminated(self) -> bool:

        return self._details.is_terminated

################################################################################
    @property
    def positions(self) -> List[Position]:

        return self._qualifications.positions

################################################################################
    @property
    def profile(self) -> Profile:

        return self.guild.profile_manager.get_profile_by_user(self._user.id)

################################################################################
    def update(self) -> None:

        self.bot.api.update_staff_member(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "positions": [p.id for p in self.positions],
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_staff_member(self.id)
        self._mgr._managed.remove(self)

################################################################################
    @property
    def characters(self) -> List[StaffCharacter]:

        return self._characters

################################################################################
    @property
    def qualifications(self) -> StaffQualifications:

        return self._qualifications

################################################################################
    async def status(self) -> Embed:

        employment_dates_string = ""
        for ep in self._details.employment_dates:
            term = U.format_dt(ep.termination_date, 'd') if ep.termination_date else "`Current`"
            employment_dates_string += f"* {U.format_dt(ep.hire_date, 'd')} - {term}\n"

        user = await self.user
        return U.make_embed(
            title=f"{self._details.name}'s Employee Record",
            description=(
                f"({user.mention})\n\n"

                f"**Birthday:** `{self._details.birthday.strftime('%m/%d') if self._details.birthday else 'Not Set'}`\n"
                f"**Employment History:**\n"
                f"{employment_dates_string}"
            ),
            fields=[
                EmbedField(
                    name="__Characters__",
                    value="\n".join(f"* `{c._details.name}`" for c in self.characters) or "`None`",
                    inline=True
                ),
                EmbedField(
                    name="__Qualifications__",
                    value="\n".join(f"* `{p.name}`" for p in self.positions) or "`None`",
                    inline=True
                ),
                EmbedField(
                    name="__Internal Notes__",
                    value=f"```{self._details.notes}```" if self._details.notes else "```None```",
                    inline=False
                ),
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return StaffMemberMenuView(user, self)

################################################################################
    async def set_name(self, interaction: Interaction) -> None:

        await self._details.set_name(interaction)

################################################################################
    async def set_birthday(self, interaction: Interaction) -> None:

        await self._details.set_birthday(interaction)

################################################################################
    async def set_qualifications(self, interaction: Interaction) -> None:

        await self._qualifications.menu(interaction)

################################################################################
    async def set_notes(self, interaction: Interaction) -> None:

        await self._details.set_notes(interaction)

################################################################################
    async def edit_employment_history(self, interaction: Interaction) -> None:

        await self._details.employment_history_menu(interaction)

################################################################################
    async def terminate(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="__Terminate Employee__",
            description="Are you sure you want to terminate this employee?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        await self._terminate()

################################################################################
    async def _terminate(self) -> None:

        self._details.get_current_employment_period().terminate()
        await self.profile.delete_post()

################################################################################
    async def admin_modify_profile(self, interaction: Interaction) -> None:

        if len(self.characters) == 1:
            character = self.characters[0]
        else:
            prompt = U.make_embed(
                title="__Modify Character Profile__",
                description=(
                    "Select the character you would like to modify.\n"
                    "This will open the character's profile menu."
                )
            )
            view = FroggeSelectView(
                interaction.user, [c.select_option() for c in self.characters]
            )

            await interaction.respond(embed=prompt, view=view)
            await view.wait()

            if not view.complete or view.value is False:
                return

            character = self.get_character(view.value)

        await character.profile.menu(interaction)

################################################################################
    def get_character(self, character_id: int) -> Optional[StaffCharacter]:

        return next((c for c in self.characters if c.id == int(character_id)), None)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self._details.name,
            value=str(self.id)
        )

################################################################################
    def profile_main_status(self) -> Embed:

        unposted_emoji = str(BotEmojis.Warning)
        posted_emoji = str(BotEmojis.Envelope)
        incomplete_emoji = str(BotEmojis.Construction)
        complete_emoji = str(BotEmojis.Check)

        character_string = ""
        for c in self.characters:
            profile = c.profile
            posted = posted_emoji if profile._post_msg.id is not None else unposted_emoji
            complete = complete_emoji if profile.is_complete() else incomplete_emoji

            character_string += f"{complete} {posted} - `{c.name}`\n"

        if not character_string:
            character_string = "`No profiles found`"

        return U.make_embed(
            title="__Staff Profiles Main Menu__",
            description=(
                "Select an option below to manage your character profile(s).\n"
                f"{U.draw_line(extra=20)}\n"
                "__**EMOJI KEY**__\n"
                f"{incomplete_emoji} - Profile incomplete\n"
                f"{unposted_emoji} - Profile not posted\n"
                f"{complete_emoji} - Profile complete\n"
                f"{posted_emoji} - Profile posted\n"
                f"{U.draw_line(extra=20)}"
            ),
            fields=[
                EmbedField(
                    name="__Character Profile Breakdown__",
                    value=character_string,
                    inline=False
                )
            ]
        )

################################################################################
    async def profile_main_menu(self, interaction) -> None:

        embed = self.profile_main_status()
        view = StaffProfilesMainMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def add_character(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Enter Character Name",
            attribute="Character Name",
            example="e.g. 'Allegro Vivo'",
            max_length=40,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        proposed_name = modal.value.strip().lower()
        if proposed_name in [c.name.lower() for c in self.characters]:
            error = U.make_error(
                title="Character Already Exists",
                message=f"You already have a character with the name '`{modal.value}`'.",
                solution="Please choose a different name."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        new_character = StaffCharacter.new(self, modal.value.strip())
        self.characters.append(new_character)

        await new_character.profile_menu(interaction)

################################################################################
    async def modify_character(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Character Profile__",
            description=(
                "Select the character you would like to modify.\n"
                "This will open the character's profile menu."
            )
        )
        view = FroggeSelectView(interaction.user, [c.select_option() for c in self.characters])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        character = self.get_character(view.value)
        await character.profile_menu(interaction)

################################################################################
    async def remove_character(self, interaction: Interaction) -> None:

        pass

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="__Remove Staff Member__",
            description="Are you sure you want to remove this staff member?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        await self._terminate()
        await interaction.respond("The staff member has been removed.", ephemeral=True)

################################################################################
    async def rehire(self, interaction: Interaction) -> None:

        self._details.employment_dates.append(EmploymentPeriod.new(self._details))
        await self.menu(interaction)

################################################################################
