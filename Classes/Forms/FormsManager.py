from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from discord import Interaction, User, Embed, SelectOption

from Classes.Common import ObjectManager
from Errors import MaxItemsReached
from UI.Common import BasicTextModal, FroggeSelectView
from UI.Forms import FormsManagerMenuView
from Utilities import Utilities as U
from .Form import Form

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("FormsManager",)

################################################################################
class FormsManager(ObjectManager):

    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

################################################################################
    async def load_all(self, payload: List[Dict[str, Any]]) -> None:

        self._managed = [Form.load(self, f) for f in payload]

        for form in self._managed:
            await form.update_post_components()

################################################################################
    @property
    def forms(self) -> List[Form]:

        return self._managed  # type: ignore

################################################################################
    async def status(self) -> Embed:

        forms_string = "\n".join(
            f"* **{f.name}**"
            for f in self.forms
        )
        if not forms_string:
            forms_string = "`No forms configured.`"

        return U.make_embed(
            title="__Forms Management__",
            description=(
                f"**[`Total Forms`]:** `{len(self.forms)}`\n\n"

                f"**[`Forms`]:**\n"
                f"{forms_string}"
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return FormsManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self.forms) >= self.MAX_ITEMS:
            error = MaxItemsReached("Form", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        modal = BasicTextModal(
            title="Enter Form Name",
            attribute="Name",
            example='e.g. "Staff Application Form"',
            max_length=80
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        form = Form.new(self, modal.value)
        self.forms.append(form)

        await form.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Form__",
            description="Pick a form from the list below to modify."
        )
        view = FroggeSelectView(interaction.user, self.form_select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        form = self[view.value]
        await form.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Form__",
            description="Pick a form from the list below to remove."
        )
        view = FroggeSelectView(interaction.user, self.form_select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        form = self[view.value]
        await form.remove(interaction)

################################################################################
    def form_select_options(self) -> List[SelectOption]:

        options = [f.select_option() for f in self.forms]
        if not options:
            options.append(
                SelectOption(
                    label="No forms available",
                    value="-1",
                    description="No forms have been configured yet."
                )
            )

        return options

################################################################################
