from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, ButtonStyle
from discord.ui import View

from UI.Common import FroggeButton

if TYPE_CHECKING:
    from Classes import Form
################################################################################

__all__ = ("FormPostView",)

################################################################################
class FormPostView(View):

    def __init__(self, form: Form):
        
        super().__init__(timeout=None)

        self.ctx: Form = form

        self.add_item(FormButton(form))
        
################################################################################
class FormButton(FroggeButton):
    
    def __init__(self, form: Form):
        
        super().__init__(
            style=ButtonStyle.primary,
            label=form.post_options.button_label or "Complete Form",
            disabled=False,
            row=0,
            custom_id=f"form:{form.id}",
            emoji=form.post_options.button_emoji
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.fill_out(interaction)

################################################################################
