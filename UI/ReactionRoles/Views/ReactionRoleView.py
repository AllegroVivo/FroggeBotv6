from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord import User, Interaction, ButtonStyle
from discord.ui import View
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ReactionRole
################################################################################

__all__ = ("ReactionRoleView",)

################################################################################
class ReactionRoleView(View):

    def __init__(self, roles: List[ReactionRole]):
        
        super().__init__(timeout=None)

        chunk_size = 5
        chunked_options = []

        for i in range(0, len(roles), chunk_size):
            chunked_options.append(roles[i:i + chunk_size])

        for idx, opts in enumerate(chunked_options):
            for role in opts:
                self.add_item(RoleButton(role, idx))
        
################################################################################
class RoleButton(FroggeButton):
    
    def __init__(self, role: ReactionRole, row: int):
        
        super().__init__(
            style=ButtonStyle.primary,
            label=role.label or "Unlabeled Role",
            disabled=False,
            row=row,
            custom_id=f"role:{role.id}"
        )

        self.role = role
        
    async def callback(self, interaction: Interaction):
        await self.role.button_callback(interaction)
        
################################################################################
