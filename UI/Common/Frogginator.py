from __future__ import annotations

from typing import Any, Optional

import discord
from discord.ext.pages import Paginator, Page
################################################################################

__all__ = ("Frogginator", )

################################################################################
class Frogginator(Paginator):
    
    def __init__(self, pages, ctx: Optional[Any] = None, **kwargs):
        
        super().__init__(
            pages=pages,
            author_check=kwargs.pop("author_check", True),
            disable_on_timeout=kwargs.pop("disable_on_timeout", True),
            use_default_buttons=kwargs.pop("use_default_buttons", True),
            default_button_row=kwargs.pop("default_button_row", 4),
            loop_pages=kwargs.pop("loop_pages", True),
            show_indicator=kwargs.pop("show_indicator", True),
            timeout=kwargs.pop("timeout", 300),
            **kwargs
        )

        self.ctx: Optional[Any] = ctx
        
################################################################################
    async def cancel(
        self,
        include_custom: bool = False,
        page: None | (str | Page | list[discord.Embed] | discord.Embed) = None,
    ) -> None:

        if page is None:
            await self.message.delete()
            return
        
        await super().cancel(include_custom, page)
            
################################################################################
    async def on_timeout(self) -> None:
        
        try:
            await super().on_timeout()
        except discord.NotFound:
            pass
        
################################################################################
        