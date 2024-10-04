from __future__ import annotations

from typing import List, TYPE_CHECKING

from Utilities import ErrorMessage

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileIncomplete",)

################################################################################
class ProfileIncomplete(ErrorMessage):

    def __init__(self, profile: Profile, requirements: List[str]):
        
        final_requirements = []
        for req in requirements:
            slot = f"_{req}"
            final = req.replace("_", " ").title()
            
            if slot in profile._details.__slots__:
                if getattr(profile._details, slot) in (None, []):
                    final_requirements.append(f"{final} - *(Details)*")
            if slot in profile._aag.__slots__:
                if getattr(profile._aag, slot) in (None, []):
                    final_requirements.append(f"{final} - *(At A Glance)*")
            if slot in profile._personality.__slots__:
                if getattr(profile._personality, slot) in (None, []):
                    final_requirements.append(f"{final} - *(Personality)*")
            if slot in profile._images.__slots__:
                if getattr(profile._images, slot) in (None, []):
                    final_requirements.append(f"{final} - *(Images)*")
        
        requirement_string = "\n".join([f"- {r}" for r in final_requirements])
        super().__init__(
            title="Profile Incomplete",
            description=(
                "*Please note profile completion requirements are decided by "
                "your venue's management team.*"
            ),
            message="Your profile is incomplete and cannot be posted.",
            solution=(
                "Please ensure that all of the following required fields are "
                "filled out and try again:\n"
                f"{requirement_string}"
            )
        )

################################################################################
