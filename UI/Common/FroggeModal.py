from __future__ import annotations

from typing import Any, Optional

from discord import Interaction
from discord.ui import Modal
################################################################################

__all__ = ("FroggeModal",)

################################################################################
class FroggeModal(Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.complete: bool = False
        self.value: Optional[Any] = None

################################################################################
    @staticmethod
    async def dummy_response(interaction: Interaction) -> None:
        
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
        