from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Dict

from discord import Interaction, User, Embed, SelectOption

from Classes.Common import ObjectManager
from Utilities import Utilities as U
from UI.Embeds import EmbedManagerMenuView
from .FroggeEmbed import FroggeEmbed
from UI.Common import FroggeSelectView
from Errors import MaxItemsReached

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("EmbedManager", )

################################################################################
class EmbedManager(ObjectManager):

    __slots__ = (
    )

    MAX_ITEMS = 80  # (4x Select Menus @ 20 items each)

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

################################################################################
    async def load_all(self, payload: List[Dict[str, Any]]) -> None:

        self._managed = [FroggeEmbed.load(self, data) for data in payload]

################################################################################
    @property
    def embeds(self) -> List[FroggeEmbed]:

        return self._managed  # type: ignore

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title="__Embeds Module Status__",
            description=(
                f"**Total Embeds:** [`{len(self._managed)}/{self.MAX_ITEMS}`]\n"
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return EmbedManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self) >= self.MAX_ITEMS:
            error = MaxItemsReached("Embeds", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        options = [
            SelectOption(
                label="Demo Embed",
                value="demo",
                description="Create a demo embed to get started."
            ),
            SelectOption(
                label="Blank Embed",
                value="blank",
                description="Start from scratch."
            )
        ]

        prompt = U.make_embed(
            title="__Add Embed__",
            description=(
                "Would you like to create a demo embed or start from scratch?"
            )
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        if view.value == "demo":
            new_embed = FroggeEmbed.demo(self)
        else:
            new_embed = FroggeEmbed.new(self)
        self._managed.append(new_embed)

        await new_embed.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Embed__",
            description=(
                "Please select an embed to modify."
            )
        )
        view = FroggeSelectView(interaction.user, [e.select_option() for e in self.embeds])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        embed = self[view.value]
        await embed.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Embed__",
            description=(
                "Please select an embed to modify."
            )
        )
        view = FroggeSelectView(interaction.user, [e.select_option() for e in self.embeds])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        embed = self[view.value]
        await embed.remove(interaction)

################################################################################
