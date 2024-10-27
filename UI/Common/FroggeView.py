from __future__ import annotations

from typing import Any, Optional

from discord import Interaction, User
from discord.ui import View
################################################################################

__all__ = ("FroggeView",)

################################################################################
class FroggeView(View):

    def __init__(
        self, 
        owner: User,
        ctx: Any, 
        *args,
        close_on_complete: bool = True,
        **kwargs
    ):
        
        super().__init__(*args, timeout=1200, **kwargs)

        self.owner: User = owner
        self.value: Optional[Any] = None
        self.complete: bool = False
        
        self.ctx: Any = ctx

        self._interaction: Optional[Interaction] = None
        self._close_on_complete: bool = close_on_complete

################################################################################
    async def interaction_check(self, interaction: Interaction) -> bool:

        if interaction.user == self.owner:
            self._interaction = interaction
            return True

        return False

################################################################################
    async def on_timeout(self) -> None:

        if self.disable_on_timeout:
            self.disable_all_items()
        else:
            self.clear_items()

        try:
            await self._interaction.edit(view=self)
        except:
            pass

################################################################################
    async def stop(self) -> None:

        super().stop()

        if self._close_on_complete:
            if self._interaction is not None:
                try:
                    await self._interaction.message.delete()
                except:
                    try:
                        await self._interaction.delete_original_response()
                    except:
                        pass

################################################################################
    def close_on_complete(self, value: bool) -> None:

        self._close_on_complete = value
        
################################################################################
    async def edit_message_helper(self, interaction: Interaction, *args, **kwargs) -> None:

        self.set_button_attributes()
        
        try:
            await interaction.edit(*args, **kwargs)
        except Exception as ex1:
            print(f"Edit Message Helper FAILED: {ex1}")
            try:
                await interaction.message.edit(*args, **kwargs)
            except Exception as ex2:
                print(f"Edit Message Helper FAILED: {ex2}")
                try:
                    await interaction.edit_original_response(*args, **kwargs)
                except Exception as ex3:
                    print(f"Edit Message Helper FAILED: {ex3}")

################################################################################
    @staticmethod
    async def dummy_response(interaction: Interaction) -> None:

        try:
            await interaction.respond("** **", delete_after=0.1)
        except:
            pass
        
################################################################################
    def set_button_attributes(self) -> None:
        
        for child in self.children:
            if hasattr(child, "set_attributes"):
                child.set_attributes()
                
################################################################################
                