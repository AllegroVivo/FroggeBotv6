from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from discord import Embed, EmbedField, Interaction

from Assets import BotEmojis
from Utilities import Utilities as U
from UI.Profiles import ProfileRequirementsToggleView

if TYPE_CHECKING:
    from Classes import ProfileManager, Profile, FroggeBot
################################################################################

__all__ = ("ProfileRequirements", )

################################################################################
class ProfileRequirements:

    # Everything besides the mgr should remain without the '_' prefix
    __slots__ = (
        "_mgr",
        # Details
        "url",
        "color",
        "jobs",
        "rates",
        # At A Glance
        "world",
        "gender",
        "race",
        "orientation",
        "height",
        "age",
        "mare",
        # Personality
        "likes",
        "dislikes",
        "personality",
        "aboutme",
        # Images
        "thumbnail",
        "main_image",
    )
    
################################################################################
    def __init__(self, mgr: ProfileManager, **kwargs) -> None:

        self._mgr: ProfileManager = mgr

        self.url: bool = kwargs.get("url", False)
        self.color: bool = kwargs.get("color", False)
        self.jobs: bool = kwargs.get("jobs", False)
        self.rates: bool = kwargs.get("rates", False)

        self.world: bool = kwargs.get("world", False)
        self.gender: bool = kwargs.get("gender", False)
        self.race: bool = kwargs.get("race", False)
        self.orientation: bool = kwargs.get("orientation", False)
        self.height: bool = kwargs.get("height", False)
        self.age: bool = kwargs.get("age", False)
        self.mare: bool = kwargs.get("mare", False)

        self.likes: bool = kwargs.get("likes", False)
        self.dislikes: bool = kwargs.get("dislikes", False)
        self.personality: bool = kwargs.get("personality", False)
        self.aboutme: bool = kwargs.get("aboutme", False)

        self.thumbnail: bool = kwargs.get("thumbnail", False)
        self.main_image: bool = kwargs.get("main_image", False)
    
################################################################################
    def load(self, data: Dict[str, Any]) -> None:
        
        for key, value in data.items():
            setattr(self, key, value)
            
################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            key: getattr(self, key)
            for key in self.__slots__[1:]
        }
    
################################################################################
    def __len__(self) -> int:

        flag = lambda x: 1 if x else 0
        return sum([flag(getattr(self, attr)) for attr in self.__slots__[1:]])

################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._mgr.guild_id
    
################################################################################
    @property
    def active_requirements(self) -> List[str]:

        return [
            attr  # .replace("_", " ").title()
            for attr in self.__slots__[1:]
            if getattr(self, attr)
        ]

################################################################################
    @staticmethod
    def emoji(value: bool) -> str:

        return str(BotEmojis.CheckGreen) if value else str(BotEmojis.CheckGray)

################################################################################

    def status(self) -> Embed:

        return U.make_embed(
            title="__Profile Requirements__",
            description=(
                "Use the buttons bellow to toggle the requirements for each "
                "section of your profile. If an item is required, it must be "
                "filled out before a profile will be posted.\n\n"

                "Note that Character Name is always required and cannot be toggled."
            ),
            fields=[
                EmbedField(
                    name="__Detail Items__",
                    value=(
                        f"{self.emoji(self.url)} - Custom URL\n"
                        f"{self.emoji(self.color)} - Accent Color\n"
                        f"{self.emoji(self.jobs)} - Jobs\n"
                        f"{self.emoji(self.rates)} - Rates"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__At A Glance Items__",
                    value=(
                        f"{self.emoji(self.gender)} - Gender/Pronouns\n"
                        f"{self.emoji(self.race)} - Race/Clan\n"
                        f"{self.emoji(self.orientation)} - Orientation\n"
                        f"{self.emoji(self.height)} - Height\n"
                        f"{self.emoji(self.age)} - Age\n"
                        f"{self.emoji(self.mare)} - Mare\n"
                        f"{self.emoji(self.world)} - Home World"
                    ),
                    inline=True
                ),
                EmbedField("** **", "** **", inline=False),
                EmbedField(
                    name="__Personality Items__",
                    value=(
                        f"{self.emoji(self.likes)} - Likes\n"
                        f"{self.emoji(self.dislikes)} - Dislikes\n"
                        f"{self.emoji(self.personality)} - Personality\n"
                        f"{self.emoji(self.aboutme)} - About Me"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Images__",
                    value=(
                        f"{self.emoji(self.thumbnail)} - Thumbnail\n"
                        f"{self.emoji(self.main_image)} - Main Image"
                    ),
                    inline=True
                )
            ]
        )

################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = ProfileRequirementsToggleView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################        
    def update(self) -> None:

        self.bot.api.update_profile_requirements(self)

################################################################################
    def toggle(self, attr: str) -> None:

        setattr(self, attr, not getattr(self, attr))
        self.update()

################################################################################
    def check(self, profile: Profile) -> bool:

        details_complete = all([
            profile._details.custom_url is not None if self.url else True,
            profile._details.color is not None if self.color else True,
            profile._details.jobs != [] if self.jobs else True,
            profile._details.rates is not None if self.rates else True
        ])

        aag_complete = all([
            profile._aag.world is not None if self.world else True,
            profile._aag.gender is not None if self.gender else True,
            profile._aag.race is not None if self.race else True,
            profile._aag.orientation is not None if self.orientation else True,
            profile._aag.height is not None if self.height else True,
            profile._aag.age is not None if self.age else True,
            profile._aag.mare is not None if self.mare else True
        ])

        personality_complete = all([
            profile._personality.likes != [] if self.likes else True,
            profile._personality.dislikes != [] if self.dislikes else True,
            profile._personality.personality is not None if self.personality else True,
            profile._personality.aboutme is not None if self.aboutme else True
        ])

        images_complete = all([
            profile._images.thumbnail is not None if self.thumbnail else True,
            profile._images.main_image is not None if self.main_image else True
        ])

        return all([details_complete, aag_complete, personality_complete, images_complete])

################################################################################
