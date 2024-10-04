from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict

from discord import User, Embed, EmbedField, Interaction, SelectOption
from dotenv.parser import Position

from Assets import BotEmojis
from Classes.Common import ObjectManager
from Errors import MaxItemsReached
from UI.Positions import PositionManagerMenuView
from Utilities import Utilities as U
from logger import log
from .Position import Position
from UI.Common import FroggeSelectView

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("PositionManager", )

################################################################################
class PositionManager(ObjectManager):

    def __init__(self, state: GuildData) -> None:
        
        super().__init__(state)
    
################################################################################
    async def load_all(self, payload: List[Dict[str, Any]]) -> None:
        
        self._managed = [Position.from_dict(i, mgr=self) for i in payload]
    
################################################################################
    @property
    def positions(self) -> List[Position]:
        
        self._managed.sort(key=lambda x: x.name or "")
        return self._managed
    
################################################################################
    async def status(self) -> Embed:

        fields = []
        halfway = self.MAX_ITEMS // 2
        if self.positions:
            pos_list1 = ""
            for pos in self.positions[:halfway]:
                pos_list1 += f"\n* {pos.name}"
                role = await pos.role
                if role is not None:
                    pos_list1 += f" - {role.mention}"
            fields.append(
                EmbedField(
                    name="__Position List:__",
                    value=pos_list1,
                    inline=True
                )
            )

            if len(self.positions) > halfway:
                pos_list2 = ""
                for pos in self.positions[halfway:]:
                    pos_list2 += f"\n* {pos.name}"
                    role = await pos.role
                    if role is not None:
                        pos_list2 += f" - {role.mention}"
                fields.append(
                    EmbedField(
                        name="** **",
                        value=pos_list2,
                        inline=True
                    )
                )

        emoji = str(BotEmojis.Cross) if len(self.positions) >= self.MAX_ITEMS else ""

        return U.make_embed(
            title="__Positions Module Status__",
            description=(
                f"**Total Positions:** [{len(self.positions)}/{self.MAX_ITEMS}] {emoji}"
            ) if self.positions else "`No Positions Created`",
            fields=fields
        )
    
################################################################################
    def get_menu_view(self, user: User) -> FroggeView:
        
        return PositionManagerMenuView(user, self)
    
################################################################################
    def select_options(self) -> List[SelectOption]:

        return [p.select_option() for p in self.positions]

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        log.info(self.guild, "Adding new position...")

        if len(self) >= self.MAX_ITEMS:
            log.warning(self.guild, "Position limit reached.")
            error = MaxItemsReached("Positions", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        new_pos = Position.new(self)
        self.positions.append(new_pos)

        log.info(self.guild, f"New position created: {new_pos.id} for guild {self.guild_id}.")

        await new_pos.menu(interaction)
        
################################################################################
    async def modify_item(self, interaction: Interaction) -> None:
        
        log.info(self.guild, f"Modifying position for guild: {self.guild_id}...")
        
        prompt = U.make_embed(
            title="__Modify Position__",
            description="Please select the position you would like to modify."
        )
        view = FroggeSelectView(interaction.user, [p.select_option() for p in self.positions])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            log.debug(self.guild, "Position modification cancelled.")
            return
        
        position = self[view.value]
        await position.menu(interaction)
        
################################################################################
    async def remove_item(self, interaction: Interaction) -> None:
        
        log.info(self.guild, "Removing position...")
        
        prompt = U.make_embed(
            title="__Remove Position__",
            description="Please select the position you would like to remove."
        )
        view = FroggeSelectView(interaction.user, [p.select_option() for p in self.positions])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            log.debug(self.guild, "Position removal cancelled.")
            return
        
        position = self[view.value]
        await position.remove(interaction)
        
################################################################################
