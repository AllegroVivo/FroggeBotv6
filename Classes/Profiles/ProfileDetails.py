from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Tuple, Dict

from discord import Colour, Interaction, EmbedField, Embed

from Assets import BotEmojis
from Errors import InvalidColor
from .ProfileSection import ProfileSection
from UI.Common import BasicTextModal, InstructionsInfo
from UI.Profiles import ProfileJobsModal, ProfileDetailsStatusView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileDetails", )

PD = TypeVar("PD", bound="ProfileDetails")

################################################################################
class ProfileDetails(ProfileSection):

    __slots__ = (
        "_name",
        "_url",
        "_color",
        "_jobs",
        "_rates",
    )
    
################################################################################
    def __init__(self, parent: Profile, **kwargs) -> None:

        super().__init__(parent)
        
        self._name: Optional[str] = kwargs.get("name", None)
        self._url: Optional[str] = kwargs.get("url", None)
        self._color: Optional[Colour] = kwargs.get("color", None)
        self._jobs: List[str] = kwargs.get("jobs", None) or []
        self._rates: Optional[str] = kwargs.get("rates", None)
    
################################################################################
    @classmethod
    def load(cls: Type[PD], parent: Profile, data: Dict[str, Any]) -> PD:
        
        return cls(
            parent=parent,
            name=data["character_name"],
            url=data["custom_url"],
            color=Colour(data["color"]) if data["color"] is not None else None,
            jobs=data["jobs"],
            rates=data["rates"]
        )
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
    
################################################################################
    @property
    def custom_url(self) -> str:
        
        return self._url
    
    @custom_url.setter
    def custom_url(self, value: Optional[str]) -> None:
        
        self._url = value
        self.update()
        
################################################################################
    @property
    def color(self) -> Colour:
        
        return self._color
    
    @color.setter
    def color(self, value: Colour) -> None:
        
        self._color = value
        self.update()
        
################################################################################
    @property
    def jobs(self) -> List[str]:
        
        return self._jobs
    
    @jobs.setter
    def jobs(self, value: List[str]) -> None:
        
        self._jobs = value
        self.update()
        
################################################################################
    @property
    def rates(self) -> str:
        
        return self._rates
    
    @rates.setter
    def rates(self, value: Optional[str]) -> None:
        
        self._rates = value
        self.update()

################################################################################
    def update(self) -> None:
    
        self.bot.api.update_profile_details(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "character_name": self.name,
            "custom_url": self.custom_url,
            "color": self.color.value if self.color is not None else None,
            "jobs": self.jobs,
            "rates": self.rates
        }

################################################################################
    def status(self) -> Embed:
    
        url_field = str(self.custom_url) if self.custom_url is not None else "`Not Set`"
        jobs = "- " + "\n- ".join(self.jobs) if self.jobs else "`Not Set`"
        rates = str(self.rates) if self.rates is not None else "`Not Set`"
        color_field = (
            f"{BotEmojis.ArrowLeft} -- (__{str(self.color).upper()}__)"
            if self._color is not None
            else "`Not Set`"
        )
    
        fields = [
            EmbedField("__Color__", color_field, True),
            EmbedField("__Jobs__", jobs, True),
            EmbedField("__Custom URL__", url_field, False),
            EmbedField("__Personal Rates__", rates, False)
        ]
    
        name = f"`{str(self.name)}`" if self.name is not None else "`Not Set`"
        char_name = f"**Character Name:** {name}"
    
        return U.make_embed(
            title="Profile Details",
            color=self.color,
            description=(
                f"{U.draw_line(text=char_name)}\n"
                f"{char_name}\n"
                f"{U.draw_line(text=char_name)}\n"
                "Select a button to add/edit the corresponding profile attribute."
            ),
            fields=fields
        )
    
################################################################################
    def compile(self) -> Tuple[
        str, Optional[str], Optional[Colour], Optional[str], Optional[EmbedField]
    ]:

        return (
            self.name,
            self.custom_url,
            self.color,
            "/".join(self._jobs) if self._jobs else None,
            EmbedField(
                name=f"{BotEmojis.FlyingMoney} __Freelance Rates__ {BotEmojis.FlyingMoney}",
                value=(
                    f"{self.rates}\n"
                    f"{U.draw_line(extra=15)}"
                ),
                inline=False
            ) if self.rates is not None else None
        )
    
################################################################################
    def progress(self) -> str:

        em_color = self.progress_emoji(self._color)
        em_name = self.progress_emoji(self._name)
        em_url = self.progress_emoji(self._url)
        em_jobs = self.progress_emoji(self._jobs)
        em_rates = self.progress_emoji(self._rates)

        return (
            f"{U.draw_line(extra=15)}\n"
            "__**Details**__\n"
            f"{em_name} -- Character Name\n"
            f"{em_url} -- Custom URL\n"
            f"{em_color} -- Accent Color\n"
            f"{em_jobs} -- Jobs List\n"
            f"{em_rates} -- Rates Field\n"
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ProfileDetailsStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_name(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Character Name",
            attribute="Name",
            cur_val=self.name,
            example="e.g. 'Allegro Vivo'",
            max_length=60,
            required=True
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.name = modal.value
    
################################################################################
    async def set_url(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Custom URL",
            attribute="URL",
            cur_val=self.custom_url,
            example="e.g. 'https://x.com/HomeHopping'",
            max_length=250,
            required=False
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        if modal.value is not None:
            url = modal.value.lower().lstrip("http").lstrip("s").lstrip("://")
            if not url.startswith("https://"):
                url = f"https://{url}"
        else:
            url = None    
        
        self.custom_url = url
    
################################################################################
    async def set_color(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Profile Accent Color",
            attribute="Accent Color HEX",
            cur_val=str(self.color).upper() if self.color is not None else None,
            example="e.g. '#4ABC23'",
            min_length=6,
            max_length=7,
            required=False,
            instructions=InstructionsInfo(
                placeholder="Enter your desired accent color.",
                value=(
                    "Enter the 6-character HEX code for your desired profile accent color.\n"
                    "Google 'Color Picker' if you have questions."
                )
            )
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        raw_color = modal.value.upper()
        if raw_color is not None and raw_color.startswith("#"):
            raw_color = raw_color[1:]
            
        try:
            color = Colour(int(raw_color, 16)) if raw_color else None
        except ValueError:
            error = InvalidColor(modal.value)
            await interaction.respond(embed=error, ephemeral=True)
        else:
            self.color = color
        
################################################################################
    async def set_jobs(self, interaction: Interaction) -> None:
        
        modal = ProfileJobsModal(self.jobs)
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.jobs = modal.value
    
################################################################################
    async def set_rates(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Personal Rates",
            attribute="Rates",
            cur_val=self.rates,
            max_length=250,
            required=False,
            multiline=True,
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.rates = modal.value
        
################################################################################
        