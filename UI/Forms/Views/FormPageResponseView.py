from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, ButtonStyle, User
from discord.ui import View

from Assets import BotEmojis
from UI.Common import FroggeButton

if TYPE_CHECKING:
    from Classes import FormQuestion
################################################################################

__all__ = ("FormPageResponseView",)

################################################################################
class FormPageResponseView(View):

    def __init__(self, question: FormQuestion):
        
        super().__init__()

        self.add_item(AnswerQuestionButton(question.id))
        self.add_item(SubmitApplicationButton())
        
################################################################################
class AnswerQuestionButton(FroggeButton):
    
    def __init__(self, question_id: str):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Respond",
            disabled=False,
            row=0
        )
        
        self.question_id: str = question_id
        
    async def callback(self, interaction: Interaction):
        question = self.view.ctx[self.question_id]
        await question.respond(interaction)

        self.view.children[1].disabled = not self.view.ctx.is_complete(interaction.user)
        
        self.view.pages[self.view.current_page] = question.page(interaction.user)
        await self.view.update(pages=self.view.pages, current_page=self.view.current_page)
        
################################################################################
class SubmitApplicationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Submit Form",
            disabled=False,
            row=0,
            emoji=BotEmojis.FlyingEnvelope
        )
        
    async def callback(self, interaction: Interaction):
        if await self.view.ctx.submit(interaction):
            await self.view.cancel()
        
################################################################################
