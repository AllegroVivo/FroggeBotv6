from __future__ import annotations

from typing import Any, Optional

from discord import ButtonStyle
from discord.ui import Button
################################################################################

__all__ = ("FroggeButton",)

################################################################################
class FroggeButton(Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

################################################################################
    def set_style(self, attribute: Optional[Any]) -> None:
        
        if isinstance(attribute, str):
            attribute = attribute.strip()
            
        self.style = ButtonStyle.secondary if not attribute else ButtonStyle.primary
            
################################################################################
    def set_attributes(self) -> None:
        """Override this to set view object-dependent attributes."""
        
        pass
    
################################################################################
    