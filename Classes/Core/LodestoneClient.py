from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

import requests
from bs4 import BeautifulSoup
from discord import Interaction

from Enums import World
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################

__all__ = ("LodestoneClient",)

################################################################################
class LodestoneClient:

    __slots__ = (
        "_state",
    )
    
    BASE_URL = "https://na.finalfantasyxiv.com/lodestone/character/"
    
################################################################################
    def __init__(self, bot: FroggeBot) -> None:

        self._state: FroggeBot = bot
    
################################################################################
    async def fetch_character_id(
        self,
        interaction: Interaction,
        forename: str,
        surname: str,
        world: World
    ) -> Optional[int]:
        
        request_url = self.BASE_URL + f"?q={forename}+{surname}&worldname={world.proper_name}"
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # Check for <p> tag with class 'parts__zero'
        no_results = soup.find('p', class_='parts__zero')
        if no_results:
            error = U.make_error(
                title="No Character Results Found",
                message=(
                    f"No character results were found for the name '{forename} {surname}' "
                    f"on the world '{world.proper_name}'."
                ),
                solution=(
                    "Please ensure the name and world are spelled correctly and "
                    "try again."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
    
        # Find <a> tag with class 'entry__link' and href pattern
        entry_links = soup.find_all('a', class_='entry__link', href=True)
        filtered_links = [
            link
            for link in entry_links 
            if re.match(r"^/lodestone/character/\d+/$", link['href'])
        ]
    
        if len(filtered_links) > 1:
            error = U.make_error(
                title="Multiple Character Results Found",
                message=(
                    f"Multiple character results were found for the name '{forename} {surname}' "
                    f"on the world '{world.proper_name}'."
                ),
                solution=(
                    "Please refine your search criteria to find the specific "
                    "character you are looking for."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
    
        # Extract the number from the href
        href = filtered_links[0]['href']
        character_id = int(href.split('/')[-2])
    
        return character_id

################################################################################
    async def fetch_character_profile(self, interaction: Interaction, char_id: int) -> Optional[BeautifulSoup]:
        
        response = requests.get(self.BASE_URL + str(char_id) + "/")
        soup = BeautifulSoup(response.text, "html.parser")

        if _ := soup.find_all('body', class_='error__body'):
            error = U.make_error(
                title="Character Profile Missing",
                description=f"Invalid Character ID: {char_id}",
                message="The character profile you are trying to access does not exist.",
                solution="Please ensure the name and world are correct and try again."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        return soup
    
################################################################################        
    async def fetch_character_bio(self, interaction: Interaction, char_id: int) -> str:
        
        soup = await self.fetch_character_profile(interaction, char_id)
        bio = soup.find("div", class_="character__selfintroduction")
        
        return bio.text
    
################################################################################
    async def fetch_character_name(self, interaction: Interaction, char_id: int) -> Optional[str]:

        soup = await self.fetch_character_profile(interaction, char_id)
        if name := soup.find("p", class_="frame__chara__name"):
            return name.text
    
################################################################################
    