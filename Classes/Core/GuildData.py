from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from discord import Guild, NotFound, Role, Member, User, Emoji, Message
from discord.abc import GuildChannel

from .GuildConfig import GuildConfiguration
from .GuildLogger import GuildLogger
from Classes.Positions.PositionManager import PositionManager
from Classes.VIPs.VIPManager import VIPManager
from Classes.Verification.VerificationManager import VerificationManager
from Classes.Profiles.ProfileManager import ProfileManager
from Classes.Staffing.StaffManager import StaffManager
from Classes.Forms.FormsManager import FormsManager
from Classes.Events.EventManager import EventManager
from Classes.Activities.GuildActivityManager import GuildActivityManager
from Classes.ReactionRoles.ReactionRoleManager import ReactionRoleManager
from Classes.Rooms.RoomsManager import RoomsManager
from Classes.Embeds.EmbedManager import EmbedManager
from Classes.Finances.FinanceManager import FinanceManager

from logger import log

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################

__all__ = ("GuildData",)

################################################################################
class GuildData:

    __slots__ = (
        "_state",
        "_parent",
        "_logger",
        "_config",
        "_position_mgr",
        "_vip_mgr",
        "_event_mgr",
        "_staff_mgr",
        "_profile_mgr",
        "_verification_mgr",
        "_activities_mgr",
        "_forms_mgr",
        "_roles_mgr",
        "_rooms_mgr",
        "_embed_mgr",
        "_finance_mgr",
    )

################################################################################
    def __init__(self, bot: FroggeBot, parent: Guild):

        self._state: FroggeBot = bot
        self._parent: Guild = parent
        
        self._config: GuildConfiguration = GuildConfiguration(self)
        self._logger: GuildLogger = GuildLogger(self)
        
        self._position_mgr: PositionManager = PositionManager(self)
        self._vip_mgr: VIPManager = VIPManager(self)
        self._verification_mgr: VerificationManager = VerificationManager(self)
        self._staff_mgr: StaffManager = StaffManager(self)
        self._profile_mgr: ProfileManager = ProfileManager(self)
        self._forms_mgr: FormsManager = FormsManager(self)
        self._event_mgr: EventManager = EventManager(self)
        self._activities_mgr: GuildActivityManager = GuildActivityManager(self)
        self._roles_mgr: ReactionRoleManager = ReactionRoleManager(self)
        self._rooms_mgr: RoomsManager = RoomsManager(self)
        self._embed_mgr: EmbedManager = EmbedManager(self)
        self._finance_mgr: FinanceManager = FinanceManager(self)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        await self._config.load(payload["configuration"])
        await self._position_mgr.load_all(payload["positions"])
        await self._vip_mgr.load_all(payload["vip_program"])
        await self._verification_mgr.load_all(payload["verification_data"])
        await self._profile_mgr.load_all(payload["profiles"])
        await self._staff_mgr.load_all(payload["staffing"])
        await self._forms_mgr.load_all(payload["forms"])
        await self._event_mgr.load_all(payload["events"])
        await self._activities_mgr.load_all(payload)  # Pass the entire payload here
        await self._roles_mgr.load_all(payload["reaction_roles"])
        await self._rooms_mgr.load_all(payload["rooms"])
        await self._embed_mgr.load_all(payload["embeds"])
        await self._finance_mgr.load_all(payload["finances"])

################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._state
    
################################################################################
    @property
    def parent(self) -> Guild:
        
        return self._parent
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._parent.id
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._parent.name
    
################################################################################
    @property
    def config(self) -> GuildConfiguration:

        return self._config
    
################################################################################
    @property
    def log(self) -> GuildLogger:

        return self._logger
    
################################################################################
    @property
    def position_manager(self) -> PositionManager:
        
        return self._position_mgr
    
###############################################################################
    @property
    def vip_manager(self) -> VIPManager:
        
        return self._vip_mgr
    
###############################################################################
    @property
    def verification_manager(self) -> VerificationManager:
        
        return self._verification_mgr
    
###############################################################################
    @property
    def staff_manager(self) -> StaffManager:
        
        return self._staff_mgr
    
###############################################################################
    @property
    def profile_manager(self) -> ProfileManager:

        return self._profile_mgr

################################################################################
    @property
    def event_manager(self) -> EventManager:

        return self._event_mgr

###############################################################################
    @property
    def forms_manager(self) -> FormsManager:

        return self._forms_mgr

###############################################################################
    @property
    def activities_manager(self) -> GuildActivityManager:

        return self._activities_mgr

###############################################################################
    @property
    def roles_manager(self) -> ReactionRoleManager:

        return self._roles_mgr

###############################################################################
    @property
    def rooms_manager(self) -> RoomsManager:

        return self._rooms_mgr

###############################################################################
    @property
    def embed_manager(self) -> EmbedManager:

        return self._embed_mgr

###############################################################################
    @property
    def finance_manager(self) -> FinanceManager:

        return self._finance_mgr

###############################################################################
    async def get_or_fetch_channel(self, channel_id: Optional[int]) -> Optional[GuildChannel]:
        
        log.debug(self, f"Fetching Channel: {channel_id}")
        
        if channel_id is None:
            return
        
        if channel := self.parent.get_channel(channel_id):
            log.debug(self, f"Channel Gotten: {channel.name}")
            return channel
        
        try:
            channel = await self.parent.fetch_channel(channel_id)
        except NotFound:
            return
        else:
            log.debug(self, f"Channel Fetched: {channel.name}")
            return channel
        
################################################################################
    async def get_or_fetch_role(self, role_id: Optional[int]) -> Optional[Role]:
        
        log.debug(self, f"Fetching Role: {role_id}")
        
        if role_id is None:
            return
        
        if role := self.parent.get_role(role_id):
            log.debug(self, f"Role Gotten: {role.name}")
            return role
        
        try:
            role = await self.parent._fetch_role(role_id)
        except NotFound:
            return
        else:
            log.debug(self, f"Role Fetched: {role.name}")
            return role
        
################################################################################
    async def get_or_fetch_member(self, user_id: int) -> Optional[Member]:
        
        log.debug(self, f"Fetching Member: {user_id}")
        
        if member := self.parent.get_member(user_id):
            log.debug(self, f"Member Gotten: {member.display_name}")
            return member
        
        try:
            member = await self.parent.fetch_member(user_id)
        except NotFound:
            return
        else:
            log.debug(self, f"Member Fetched: {member.display_name}")
            return member
        
################################################################################
    async def get_or_fetch_member_or_user(self, user_id: int) -> Optional[Union[Member, User]]:
        
        log.debug(self, f"Fetching Member or User: {user_id}")
        
        if member := await self.get_or_fetch_member(user_id):
            return member
        
        if user := self._state.get_user(user_id):
            log.debug(self, f"User Gotten: {user.name}")
            return user
        
        try:
            user = await self._state.fetch_user(user_id)
        except NotFound:
            return
        else:
            log.debug(self, f"User Fetched: {user.name}")
            return user
        
################################################################################
    async def get_or_fetch_emoji(self, emoji_id: int) -> Optional[Emoji]:
        
        log.debug(self, f"Fetching Emoji: {emoji_id}")
        
        for emoji in self.parent.emojis:
            if emoji.id == emoji_id:
                return emoji
        
        try:
            return await self.parent.fetch_emoji(emoji_id)
        except NotFound:
            return
        
################################################################################
    async def get_or_fetch_message(self, message_url: Optional[str]) -> Optional[Message]:
        
        log.debug(self, f"Fetching Message: {message_url}")
        
        if message_url is None:
            return
        
        url_parts = message_url.split("/")
        
        if message := self.bot.get_message(int(url_parts[-1])):
            return message
        
        if channel := await self.get_or_fetch_channel(int(url_parts[-2])):
            try:
                return await channel.fetch_message(int(url_parts[-1]))  # type: ignore
            except NotFound:
                return
        
################################################################################
