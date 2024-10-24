from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Dict, Any, Optional

from discord import User, Embed, SelectOption, Interaction
from .CharacterDetails import CharacterDetails
from Classes.Common import Identifiable
from UI.Common import ConfirmCancelView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import StaffMember, Profile
################################################################################

__all__ = ("StaffCharacter", )

SC = TypeVar("SC", bound="StaffCharacter")

################################################################################
class StaffCharacter(Identifiable):

    __slots__ = (
        "_parent",
        "_details",
        "_profile_id",
    )

################################################################################
    def __init__(self, parent: StaffMember, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: StaffMember = parent
        self._details: CharacterDetails = CharacterDetails(self, name=kwargs.get("name"))
        self._profile_id: int = kwargs.get("profile_id")

################################################################################
    @classmethod
    def new(cls: Type[SC], parent: StaffMember, name: str) -> SC:

        profile = parent.guild.profile_manager._new_profile(parent._user.id)
        data = parent.bot.api.create_staff_character(parent.id, name, profile.id)

        self: SC = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent

        self._details = CharacterDetails(self, name=name)
        self._profile_id = data["profile_id"]

        return self

################################################################################
    @classmethod
    def load(cls: Type[SC], parent: StaffMember, data: Dict[str, Any]) -> SC:

        self: SC = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent

        self._details = CharacterDetails(self, name=data["name"])
        self._profile_id = data["profile_id"]

        return self

################################################################################
    @property
    def name(self) -> str:

        return self._details.name

################################################################################
    @property
    def profile(self) -> Optional[Profile]:

        if self._profile_id is None:
            return

        return self._parent.guild.profile_manager[self._profile_id]

################################################################################
    def delete(self) -> None:

        self._parent.bot.api.delete_staff_character(self.id)
        self._parent._characters.remove(self)

################################################################################
    def select_option(self) -> SelectOption:

        return SelectOption(
            label=self._details.name,
            value=str(self.id),
        )

################################################################################
    async def profile_menu(self, interaction: Interaction) -> None:

        await self.profile.menu(interaction)

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="__Remove Character__",
            description=f"Are you sure you want to remove the character `{self.name}`?"
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
