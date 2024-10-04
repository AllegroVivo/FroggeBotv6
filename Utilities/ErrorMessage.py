from __future__ import annotations

from datetime import datetime
from typing import Optional

from discord import Embed, Colour

from Assets import BotImages
################################################################################

__all__ = ("ErrorMessage", )

################################################################################
class ErrorMessage(Embed):
    """A subclassed Discord embed object acting as an error message."""

    def __init__(
        self,
        *,
        title: str,
        message: str,
        solution: str,
        description: Optional[str] = None
    ):

        super().__init__(
            title=title,
            description=description,
            colour=Colour.red()
        )

        self.add_field(
            name="What Happened?",
            value=message,
            inline=True,
        )

        self.add_field(
            name="How to Fix?",
            value=solution,
            inline=True
        )

        self.timestamp = datetime.now()
        self.set_thumbnail(url=BotImages.ErrorFrog)
        
################################################################################
        