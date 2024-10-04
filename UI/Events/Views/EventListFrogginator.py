from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord.ext.pages import Page

from UI.Common import Frogginator

if TYPE_CHECKING:
    from Classes import EventManager
################################################################################

__all__ = ("EventListFrogginator",)

################################################################################
class EventListFrogginator(Frogginator):
    
    def __init__(self, pages: List[Page], mgr: EventManager):
        
        super().__init__(pages=pages, loop_pages=True, default_button_row=3)
        self.ctx: EventManager = mgr

################################################################################
 