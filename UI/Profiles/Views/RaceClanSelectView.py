from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, User
from discord.ui import Select

from UI.Common import FroggeView, CloseMessageButton
from UI.Profiles import CustomRaceClanModal, CustomClanModal
from Enums import Race, Clan

if TYPE_CHECKING:
    from Classes import ProfileAtAGlance
################################################################################

__all__ = ("RaceClanSelectView",)

################################################################################        
class RaceClanSelectView(FroggeView):

    def __init__(self, user: User, aag: ProfileAtAGlance):

        super().__init__(user, aag)

        item_list = [
            RaceSelect(),
            CloseMessageButton()
        ]
        for item in item_list:
            self.add_item(item)

################################################################################        
class RaceSelect(Select):

    def __init__(self):
        super().__init__(
            placeholder="Select Your Race...",
            options=Race.select_options(),
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        aag = self.view.ctx
        response = Race(int(self.values[0]))

        if response is Race.Custom:
            modal = CustomRaceClanModal(aag.race, aag.clan)

            await interaction.response.send_modal(modal)
            await modal.wait()

            if modal.complete:
                self.view.value = (modal.value[0], modal.value[1])
                self.view.complete = True

            await self.view.stop()  # type: ignore
            return

        await interaction.response.edit_message()

        self.view.value = response
        self.placeholder = response.proper_name
        self.disabled = True
        self.view.add_item(ClanSelect(response))

        await self.view.edit_message_helper(interaction, view=self.view)

################################################################################
class ClanSelect(Select):

    def __init__(self, race: Race):
        
        super().__init__(
            placeholder="Select Your Clan...",
            options=Clan.select_options_by_race(race),
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        aag = self.view.ctx
        response = Clan(int(self.values[0]))

        if response is Clan.Custom:
            modal = CustomClanModal(aag._clan)

            await interaction.response.send_modal(modal)
            await modal.wait()

            if modal.complete:
                response = modal.value
        else:
            await interaction.response.edit_message()    

        self.view.value = (self.view.value, response)
        self.view.complete = True

        await self.view.stop()  # type: ignore

################################################################################
