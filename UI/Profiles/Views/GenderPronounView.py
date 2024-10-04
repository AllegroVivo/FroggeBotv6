from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, User
from discord.ui import Select

from UI.Common import FroggeView, CloseMessageButton
from UI.Profiles import CustomGenderModal
from Enums import Gender, Pronoun

if TYPE_CHECKING:
    from Classes import ProfileAtAGlance
################################################################################

__all__ = ("GenderPronounView",)

################################################################################        
class GenderPronounView(FroggeView):

    def __init__(self, user: User, aag: ProfileAtAGlance):

        super().__init__(user, aag)

        item_list = [
            GenderSelect(),
            CloseMessageButton()
        ]
        for item in item_list:
            self.add_item(item)

################################################################################        
class GenderSelect(Select):

    def __init__(self):
        super().__init__(
            placeholder="Select your preferred gender...",
            options=Gender.select_options(),
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        gender = Gender(int(self.values[0]))        
        if gender != Gender.Custom:
            await interaction.response.edit_message()
        else:
            modal = CustomGenderModal(self.view.ctx.gender)

            await interaction.response.send_modal(modal)
            await modal.wait()

            if not modal.complete:
                await self.view.stop()  # type: ignore
                return

            gender = modal.value

        self.view.value = gender
        self.placeholder = gender.proper_name if isinstance(gender, Gender) else gender
        self.disabled = True
        
        self.view.add_item(PronounSelect())

        await self.view.edit_message_helper(interaction=interaction, view=self.view)

################################################################################
class PronounSelect(Select):

    def __init__(self):
        super().__init__(
            placeholder="Select your preferred pronouns...",
            options=Pronoun.select_options(),
            max_values=len(Pronoun.select_options()),
            row=1
        )

    async def callback(self, interaction: Interaction):
        pronouns = [Pronoun(int(i)) for i in self.values]
        
        self.view.value = (self.view.value, pronouns)
        self.view.complete = True

        await interaction.response.edit_message()
        await self.view.stop()  # type: ignore

################################################################################
