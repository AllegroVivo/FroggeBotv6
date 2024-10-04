from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, List, Optional, Union, Type

from discord import Interaction, TextChannel, ForumChannel, ChannelType
from discord.ext.pages import Page

from Classes.Common import ObjectManager, LazyChannel
from UI.Common import FroggeSelectView, Frogginator
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData, BaseActivity
################################################################################

__all__ = ("ActivityManager", )

################################################################################
class ActivityManager(ObjectManager, ABC):

    __slots__ = (
        "_channel",
        "_type",
    )

################################################################################
    def __init__(self, state: GuildData, managed_type: Type[BaseActivity], **kwargs) -> None:

        super().__init__(state)

        self._type: Type[BaseActivity] = managed_type
        self._channel: LazyChannel = LazyChannel(self, kwargs.get("channel_id"))
    
################################################################################
    @property
    def activity_name(self) -> str:
        
        return self.__class__.__name__.replace("Manager", "")
    
################################################################################
    @property
    def all_items(self) -> List[BaseActivity]:

        return self._managed  # type: ignore

################################################################################
    @property
    def active_items(self) -> List[BaseActivity]:

        return [g for g in self._managed if g.is_active()]  # type: ignore

################################################################################
    @property
    async def channel(self) -> Union[TextChannel, ForumChannel]:

        return await self._channel.get()

    @channel.setter
    def channel(self, value: Union[TextChannel, ForumChannel]) -> None:

        self._channel.set(value)

################################################################################
    async def paginate_items(self, interaction: Interaction) -> None:
        
        pages = [item.page() for item in self.active_items]
        if not pages:
            pages.append(
                Page(
                    embeds=[
                        U.make_embed(
                            title=f"No Active {self.activity_name.title()}",
                            description=(
                                f"There are currently no active {self.activity_name.lower()}s."
                            )
                        )
                    ]
                )
            )
        
        frogginator = Frogginator(pages)
        await frogginator.respond(interaction)
    
################################################################################
    async def _select_item(self, interaction: Interaction, action: str) -> Optional[int]:

        prompt = U.make_embed(
            title=f"__{action.title()} {self.activity_name.title()}__",
            description=(
                f"Please select the {self.activity_name.lower()} "
                f"you would like to {action.lower()}."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[g.select_option() for g in self.active_items]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        return int(view.value)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self.active_items) >= self.MAX_ITEMS:
            error = U.make_error(
                title=f"Max Concurrent {self.activity_name.title()}s Reached",
                description=f"**Maximum Concurrent {self.activity_name.title()}s:** `{self.MAX_ITEMS}`",
                message=f"You cannot create any more active {self.activity_name.lower()}s.",
                solution=(
                    f"You can wait for one of the current {self.activity_name.lower()}s to end or "
                    f"deactivate one of the current {self.activity_name.lower()}s."
                )
            )
            await interaction.respond(embed=error)
            return

        item = self._type.new(self)  # type: ignore
        self._managed.append(item)

        await item.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        item_id = await self._select_item(interaction, "Modify")
        if item_id is None:
            return

        item = self[item_id]
        await item.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        item_id = await self._select_item(interaction, "Remove")
        if item_id is None:
            return

        item = self[item_id]
        await item.remove(interaction)

################################################################################
    async def set_channel(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title=f"__Set {self.activity_name.title()} Channel__",
            description=(
                f"Please select the channel where you would like to manage/post "
                f"`{self.activity_name.lower()}s`."
            )
        )
        channel = await U.listen_for(
            interaction=interaction,
            prompt=prompt,
            mentionable_type=U.MentionableType.Channel,
            channel_restrictions=[ChannelType.text, ChannelType.forum]
        )
        if channel is None:
            return

        self.channel = channel

################################################################################
    