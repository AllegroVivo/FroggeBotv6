from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from discord import Interaction, Role

from Classes.Common import LazyRole

if TYPE_CHECKING:
    from Classes import VerificationManager, FroggeBot, GuildData
################################################################################

__all__ = ("VerificationConfig", )

################################################################################
class VerificationConfig:

    __slots__ = (
        "_mgr",
        "_log_events",
        "_require_captcha",
        "_require_2fa",
        "_change_name",
        "_role",
    )
    
################################################################################
    def __init__(self, mgr: VerificationManager, **kwargs) -> None:

        self._mgr: VerificationManager = mgr

        self._log_events: bool = kwargs.get("log_events", True)
        self._require_captcha: bool = kwargs.get("require_capcha", True)
        self._require_2fa: bool = kwargs.get("require_2fa", True)
        self._change_name: bool = kwargs.get("change_name", True)
        self._role: LazyRole = LazyRole(self, kwargs.get("role_id"))
    
################################################################################
    def load(self, data: Dict[str, Any]) -> None:
        
        self._log_events = data["log_events"]
        self._require_captcha = data["show_captcha"]
        self._require_2fa = data["user_two_factor"]
        self._change_name = data["change_nickname"]
        self._role = LazyRole(self, data.get("role_id"))
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:

        return self._mgr.guild

################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._mgr.guild_id
    
################################################################################
    @property
    def log_events(self) -> bool:

        return self._log_events

    @log_events.setter
    def log_events(self, value: bool) -> None:

        self._log_events = value
        self.update()

################################################################################
    @property
    def require_captcha(self) -> bool:

        return self._require_captcha

    @require_captcha.setter
    def require_captcha(self, value: bool) -> None:

        self._require_captcha = value
        self.update()

################################################################################
    @property
    def require_2fa(self) -> bool:

        return self._require_2fa

    @require_2fa.setter
    def require_2fa(self, value: bool) -> None:

        self._require_2fa = value
        self.update()
        
################################################################################
    @property
    def change_name(self) -> bool:

        return self._change_name

    @change_name.setter
    def change_name(self, value: bool) -> None:

        self._change_name = value
        self.update()

################################################################################
    @property
    async def role(self) -> Optional[Role]:

        return await self._role.get()

    @role.setter
    def role(self, value: Role) -> None:

        self._role.set(value)

################################################################################
    def update(self) -> None:

        self.bot.api.update_verification_config(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "log_events": self.log_events,
            "show_captcha": self.require_captcha,
            "user_two_factor": self.require_2fa,
            "change_nickname": self.change_name,
            "role_id": self._role.id
        }
    
################################################################################
    async def toggle_logging(self, interaction: Interaction) -> None:

        self.log_events = not self.log_events
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def toggle_captcha(self, interaction: Interaction) -> None:

        self.require_captcha = not self.require_captcha
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def toggle_change_name(self, interaction: Interaction) -> None:

        self.change_name = not self.change_name
        await interaction.respond("** **", delete_after=0.1)

################################################################################
    async def toggle_2fa(self, interaction: Interaction) -> None:

        self.require_2fa = not self.require_2fa
        await interaction.respond("** **", delete_after=0.1)

################################################################################
