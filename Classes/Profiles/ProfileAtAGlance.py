from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Optional, List, Union, Type, TypeVar, Any, Dict

from discord import Interaction, Embed, EmbedField

from Assets import BotEmojis
from Enums import (
    GameWorld,
    Gender,
    Pronoun,
    Race,
    Orientation,
    Clan,
    FroggeEnum,
    DataCenter,
)
from UI.Common import BasicTextModal, InstructionsInfo
from UI.Profiles import (
    ProfileAtAGlanceStatusView,
    HomeWorldSelectView,
    GenderPronounView,
    RaceClanSelectView,
    OrientationSelectView
)
from Utilities import Utilities as U
from .ProfileSection import ProfileSection

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileAtAGlance",)

AAG = TypeVar("AAG", bound="ProfileAtAGlance")

################################################################################
class ProfileAtAGlance(ProfileSection):

    __slots__ = (
        "_world",
        "_gender",
        "_pronouns",
        "_race",
        "_clan",
        "_orientation",
        "_height",
        "_age",
        "_mare",
    )
    
################################################################################
    def __init__(self, parent: Profile, **kwargs) -> None:

        super().__init__(parent)
        
        self._world: Optional[GameWorld] = kwargs.get("world")
        self._gender: Optional[Union[Gender, str]] = kwargs.get("gender", None)
        self._pronouns: List[Pronoun] = kwargs.get("pronouns", None) or []
        self._race: Optional[Union[Race, str]] = kwargs.get("race", None)
        self._clan: Optional[Union[Clan, str]] = kwargs.get("clan", None)
        self._orientation: Optional[Union[Orientation, str]] = kwargs.get("orientation", None)
        self._height: Optional[int] = kwargs.get("height", None)
        self._age: Optional[Union[str, int]] = kwargs.get("age", None)
        self._mare: Optional[str] = kwargs.get("mare", None)
    
################################################################################
    @classmethod
    def load(cls: Type[AAG], parent: Profile, data: Dict[str, Any]) -> AAG:
        
        return cls(
            parent=parent,
            world=GameWorld(data["world"]) if data["world"] is not None else None,
            gender=(
                Gender(int(data["gender"]))
                if data["gender"].isdigit() and int(data["gender"]) < Gender.Custom.value 
                else data["gender"]
            ) if data["gender"] is not None else None,
            pronouns=[Pronoun(p) for p in data["pronouns"]] if data["pronouns"] is not None else [],
            race=(
                Race(int(data["race"]))
                if data["race"].isdigit() and int(data["race"]) < Race.Custom.value
                else data["race"]
            ) if data["race"] is not None else None,
            clan=(
                Clan(int(data["clan"]))
                if data["clan"].isdigit() and int(data["clan"]) < Clan.Custom.value
                else data["clan"]
            ) if data["clan"] is not None else None,
            orientation=(
                Orientation(int(data["orientation"]))
                if data["orientation"].isdigit() and int(data["orientation"]) < Orientation.Custom.value
                else data["orientation"]
            ) if data["orientation"] is not None else None,
            height=data["height"],
            age=data["age"],
            mare=data["mare"]
        )
    
################################################################################
    @property
    def world(self) -> Optional[GameWorld]:
    
        return self._world
    
    @world.setter
    def world(self, value: Optional[GameWorld]) -> None:
        
        self._world = value
        self.update()
        
################################################################################
    @property
    def gender(self) -> Optional[Union[Gender, str]]:
        
        return self._gender
    
    @gender.setter
    def gender(self, value: Optional[Union[Gender, str]]) -> None:
        
        self._gender = value
        self.update()
        
################################################################################
    @property
    def pronouns(self) -> List[Pronoun]:
        
        return self._pronouns
    
    @pronouns.setter
    def pronouns(self, value: List[Pronoun]) -> None:
        
        self._pronouns = value
        self.update()
        
################################################################################
    @property
    def race(self) -> Optional[Union[Race, str]]:
        
        return self._race
    
    @race.setter
    def race(self, value: Optional[Union[Race, str]]) -> None:
        
        self._race = value
        self.update()
        
################################################################################
    @property
    def clan(self) -> Optional[Union[Clan, str]]:
        
        return self._clan
    
    @clan.setter
    def clan(self, value: Optional[Union[Clan, str]]) -> None:
        
        self._clan = value
        self.update()
        
################################################################################
    @property
    def orientation(self) -> Optional[Union[Orientation, str]]:
        
        return self._orientation
    
    @orientation.setter
    def orientation(self, value: Optional[Union[Orientation, str]]) -> None:
        
        self._orientation = value
        self.update()
        
################################################################################
    @property
    def height(self) -> Optional[int]:
        
        return self._height
    
    @height.setter
    def height(self, value: Optional[int]) -> None:
        
        self._height = value
        self.update()
        
################################################################################
    @property
    def age(self) -> Optional[Union[str, int]]:
        
        return self._age
    
    @age.setter
    def age(self, value: Optional[Union[str, int]]) -> None:
        
        self._age = value
        self.update()

################################################################################
    @property
    def mare(self) -> Optional[str]:
        
        return self._mare
    
    @mare.setter
    def mare(self, value: Optional[str]) -> None:
        
        self._mare = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.api.update_profile_ataglance(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "world": self._world.value if self._world is not None else None,
            "gender": str(
                self._gender.value
                if isinstance(self._gender, FroggeEnum)
                else self._gender
            ),
            "pronouns": [p.value for p in self._pronouns],
            "race": str(
                self._race.value
                if isinstance(self._race, FroggeEnum)
                else self._race
            ),
            "clan": str(
                self._clan.value
                if isinstance(self._clan, FroggeEnum)
                else self._clan
            ),
            "orientation": str(
                self._orientation.value
                if isinstance(self._orientation, FroggeEnum)
                else self._orientation
            ),
            "height": self._height,
            "age": str(self._age),
            "mare": self._mare
        }
    
################################################################################
    @staticmethod
    def get_attribute_str(attr: Any) -> str:

        if not attr:
            return "`Not Set`"
        elif isinstance(attr, FroggeEnum):
            return attr.proper_name
        elif isinstance(attr, int):
            return str(attr)
        elif isinstance(attr, str):
            return attr
        elif isinstance(attr, list):
            return "/".join([p.proper_name for p in attr])
        else:
            raise ValueError(f"Invalid attribute type: {type(attr)}")

################################################################################
    def format_height(self) -> str:

        if self.height is None:
            return "`Not Set`"

        inches = int(self._height / 2.54)
        feet = int(inches / 12)
        leftover = int(inches % 12)

        return f"{feet}' {leftover}\" (~{self.height} cm.)"

################################################################################
    def status(self) -> Embed:

        race_val = self.get_attribute_str(self.race)
        clan_val = self.get_attribute_str(self.clan)

        raceclan = f"{race_val}/{clan_val}"
        if isinstance(self.race, str) or isinstance(self.clan, str):
            raceclan += "\n*(Custom Value(s))*"

        gender_val = self.get_attribute_str(self.gender)
        pronoun_val = self.get_attribute_str(self.pronouns)

        gp_combined = f"{gender_val} -- *({pronoun_val})*"
        if isinstance(self.gender, str):
            gp_combined += "\n*(Custom Value)*"

        orientation_val = self.get_attribute_str(self.orientation)
        if isinstance(self.orientation, str):
            orientation_val += "\n*(Custom Value)*"

        height_val = self.format_height()
        age_val = self.get_attribute_str(self.age)
        mare_val = self.get_attribute_str(self.mare)

        data_center = DataCenter.from_world(self.world) if self.world is not None else None
        dc_name = f", {data_center.proper_name}" if data_center is not None else ""
        if data_center in (DataCenter.Aether, DataCenter.Crystal, DataCenter.Dynamis, DataCenter.Primal):
            region = ", NA"
        elif data_center in (DataCenter.Light, DataCenter.Chaos):
            region = ", EU"
        elif data_center == DataCenter.Materia:
            region = ", OC"
        elif data_center in (DataCenter.Elemental, DataCenter.Gaia, DataCenter.Mana, DataCenter.Meteor):
            region = ", JP"
        else:
            region = ""
        world_val = f"{self.get_attribute_str(self.world)}{dc_name}{region}"

        fields = [
            EmbedField("__Race/Clan__", raceclan, True),
            EmbedField("__Gender/Pronouns__", gp_combined, True),
            EmbedField("", U.draw_line(extra=30), False),
            EmbedField("__Orientation__", orientation_val, True),
            EmbedField("__Mare ID__", mare_val, True),
            EmbedField("", U.draw_line(extra=30), False),
            EmbedField("__Height__", height_val, True),
            EmbedField("__RP Age__", age_val, True),
            EmbedField("", U.draw_line(extra=30), False),
            EmbedField("__Home World__", world_val, True),
        ]

        return U.make_embed(
            color=self.parent.color,
            title=f"At A Glance Section Details for {self.parent.name}",
            description=(
                "*(Click the corresponding button below to edit each data point.)*\n"
                f"{U.draw_line(extra=38)}"
            ),
            fields=fields,
            timestamp=False
        )
    
################################################################################
    def _raw_string(self) -> str:
        
        ret = ""
        
        if self.world is not None:
            world = self._world.proper_name if isinstance(self._world, GameWorld) else self._world
            ret += f"__Home World:__ {world}\n"

        if self.gender is not None:
            gender = self._gender.proper_name if isinstance(self._gender, Gender) else self._gender
            ret += f"__Gender:__ {gender}"
            
            if self.pronouns:
                pronouns = "/".join([p.proper_name for p in self._pronouns])
                ret += f" -- *({pronouns})*"
                
            ret += "\n"
            
        if self.race is not None:
            race = self._race.proper_name if isinstance(self._race, Race) else self._race
            ret += f"__Race:__ {race}"
    
            if self.clan is not None:
                clan = self._clan.proper_name if isinstance(self._clan, Clan) else self._clan
                ret += f" / {clan}"
    
            ret += "\n"
            
        if self.orientation is not None:
            orientation = (
                self._orientation.proper_name
                if isinstance(self._orientation, Orientation)
                else self._orientation
            )
            ret += f"__Orientation:__ {orientation}\n"
            
        if self.height is not None:
            ret += f"__Height:__ {self.format_height()}\n"
            
        if self.age is not None:
            ret += f"__RP Age:__ `{self.age}`\n"
            
        if self.mare is not None:
            ret += f"__Mare ID:__ `{self.mare}`\n"

        if ret:
            ret += U.draw_line(extra=15)

        return ret

################################################################################
    def compile(self) -> Optional[EmbedField]:

        if not self._raw_string():
            return

        return EmbedField(
            name=f"{BotEmojis.Eyes}  __At A Glance__ {BotEmojis.Eyes}",
            value=self._raw_string(),
            inline=False
    )
    
################################################################################
    def progress(self) -> str:

        em_world = self.progress_emoji(self._world)
        em_gender = self.progress_emoji(self._gender)
        em_race = self.progress_emoji(self._race)
        em_orientation = self.progress_emoji(self._orientation)
        em_height = self.progress_emoji(self._height)
        em_age = self.progress_emoji(self._age)
        em_mare = self.progress_emoji(self._mare)

        return (
            f"{U.draw_line(extra=15)}\n"
            "__**At A Glance**__\n"
            f"{em_world} -- Home World\n"
            f"{em_gender} -- Gender / Pronouns\n"
            f"{em_race} -- Race / Clan\n"
            f"{em_orientation} -- Orientation\n"
            f"{em_height} -- Height\n"
            f"{em_age} -- RP Age\n"
            f"{em_mare} -- Friend ID\n"
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ProfileAtAGlanceStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_world(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__World Selection__",
            description=(
                "Please first select your data center followed by the world "
                "in which your character resides. "
            )
        )
        view = HomeWorldSelectView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        _, world = view.value
        self.world = world
    
################################################################################
    async def set_raceclan(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Select Your Race & Clan",
            description=(
                "Pick your character's race from the drop-down below.\n"
                "An additional selector will then appear for you to choose your clan.\n\n"

                "**If none of those apply, you may select `Custom`, and a pop-up will\n"
                "appear for you to enter your own custom information into.**"
            )
        )
        view = RaceClanSelectView(interaction.user, self)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self._race = view.value[0]
        self.clan = view.value[1]
    
################################################################################
    async def set_gender(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Gender/Pronoun Selection",
            description=(
                "Pick your preferred gender from the selector below.\n"
                "Don't worry,  you'll be able to choose your pronouns next!\n\n"

                "**If you select `Custom`, a pop-up will appear for you\n"
                "to provide your custom gender text.**"
            )
        )
        view = GenderPronounView(interaction.user, self)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self._gender = view.value[0]  # Don't bother doing a database hit here
        self.pronouns = view.value[1]
    
################################################################################
    async def set_orientation(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Select Your Orientation",
            description=(
                "Pick your preferred orientation from the selector below.\n\n"

                "**If you select `Custom`, a pop-up will appear for\n"
                "you to provide your custom orientation value.**"
            )
        )
        view = OrientationSelectView(interaction.user, self)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.orientation = view.value
    
################################################################################
    async def set_height(self, interaction: Interaction) -> None:

        if self.height is not None:
            inches = int(self.height / 2.54)
            feet = int(inches / 12)
            leftover = int(inches % 12)
            cur_val = f"{feet}' {leftover}\""
        else:
            cur_val = None

        modal = BasicTextModal(
            title="Height Entry",
            attribute="Height",
            cur_val=cur_val,
            example="eg. '6ft 2in'",
            required=False,
            max_length=20,
            instructions=InstructionsInfo(
                placeholder="Enter your height in feet and inches.",
                value="Enter your height in feet and inches, or centimeters."
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        raw = modal.value
        if raw is None:
            self.height = None
            return

        # RegEx Explanation: This RegEx pattern is designed to match a variety of
        # height input formats, including:
        # - A single number followed by "cm" or "cm."
        # - A single number followed by "ft", "feet", or "'"
        # - A single number followed by "in", "inches", or "''"
        # - A combination of the above three formats, separated by spaces
        result = re.match(
            r"^(\d+)\s*cm\.?|(\d+)\s*(?:ft\.?|feet|')$|(\d+)\s*(?:in\.?|inches|\"|'')|"
            r"(\d+)\s*(?:ft\.?|feet|')\s*(\d+)\s*(?:in\.?|inches|\"|'')",
            raw
        )

        if not result:
            error = U.make_error(
                title="Invalid Height Input",
                message=f"The value `{raw}` couldn't be interpreted.",
                solution=(
                    "The following are acceptable input styles:\n"
                    "- `X feet X inches`\n"
                    "- `X ft. X in.`\n"
                    "- `X in.`\n"
                    "- `X cm.`"
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        if result.group(1):
            self.height = int(result.group(1))
        elif result.group(2):
            cm = int(result.group(2)) * 12 * 2.54
            self.height = math.ceil(cm)
        elif result.group(3):
            cm = int(result.group(3)) * 2.54
            self.height = math.ceil(cm)
        elif result.group(4) and result.group(5):
            inches = int(result.group(4)) * 12 + int(result.group(5))
            self.height = math.ceil(inches * 2.54)
    
################################################################################
    async def set_age(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Age Value Input",
            attribute="Age",
            cur_val=str(self.age) if self.age is not None else None,
            example="eg. '32' -or- 'Older than you think...'",
            max_length=30,
            required=False,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        if modal.value is not None and modal.value.isdigit():
            value = abs(int(modal.value))
        else:
            value = modal.value

        self.age = value
    
################################################################################
    async def set_mare(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Mare ID Code Entry",
            attribute="Mare ID",
            cur_val=self.mare,
            example="eg. 'A1B2C3D4E5'",
            required=False,
            max_length=30,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.mare = modal.value
    
################################################################################
    