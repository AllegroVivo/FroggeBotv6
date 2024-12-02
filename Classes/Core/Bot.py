from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime
from typing import TYPE_CHECKING
import json

import pytz
from discord import Attachment, Bot, TextChannel, ApplicationContext, DiscordException, File, Interaction

from Assets import BotImages
from logger import log
from .APIClient import APIClient
from .GuildManager import GuildManager
from .LodestoneClient import LodestoneClient
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################

__all__ = ("FroggeBot",)

################################################################################
class FroggeBot(Bot):

    __slots__ = (
        "_img_dump",
        "_error_dump",
        "_guild_mgr",
        "_lodestone",
        "_api",
    )
    
    IMAGE_DUMP = 991902526188302427
    ERROR_OUT = 974493350919045190

################################################################################
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._img_dump: TextChannel = None  # type: ignore
        self._error_dump: TextChannel = None  # type: ignore
      
        self._guild_mgr: GuildManager = GuildManager(self)
        self._lodestone: LodestoneClient = LodestoneClient(self)
        self._api: APIClient = APIClient(self)
        
################################################################################
    def __getitem__(self, guild_id: int) -> GuildData:
        
        return self._guild_mgr[guild_id]
    
################################################################################
    def __iter__(self):
        
        return iter(self._guild_mgr)
    
################################################################################
    @property
    def guild_manager(self) -> GuildManager:
        
        return self._guild_mgr
    
################################################################################
    @property
    def lodestone(self) -> LodestoneClient:
        
        return self._lodestone
    
################################################################################
    @property
    def api(self) -> APIClient:
        
        return self._api
    
################################################################################
    async def load_all(self) -> None:

        log.info(None, "Initializing... Fetching dump channels...")
        # Dump channels can be hard-coded since they'll always be guaranteed.
        self._img_dump = await self.fetch_channel(self.IMAGE_DUMP)
        self._error_dump = await self.fetch_channel(self.ERROR_OUT)

        log.info(None, "Loading all Frogge Guilds...")
        
        for guild in self.guilds:
            self._guild_mgr.init_guild(guild)
        
        log.info(None, "Retrieving full API payload...")
        payload = self.api.load_all()
        
        #NH: Be aware this will create and write the RuntimeLogs/ folder to the cwd. 
        try:
            log_folder = "RuntimeLogs/"
            file_path = log_folder + "payload.json"
            os.makedirs(log_folder, exist_ok=True)
            with open(file_path, 'w+', encoding='utf8') as file:
                file.write(json.dumps(payload))
                log.info(None, f'Wrote payload to {file_path}')
        except OSError as e:
            log.error(None, f'Error reading or writing to {file_path}: {e.args}')
        
        for data in payload:
            frogge = self[data["id"]]
            if frogge is None:
                continue
            await frogge.load_all(data["data"])
            log.info(None, f"Loaded guild {frogge.name} ({frogge.guild_id})...")

        log.info(None, "Done!")
    
################################################################################
    async def dump_image(self, image: Attachment) -> str:
        """Dumps an image into the image dump channel and returns the URL.
        
        Parameters:
        -----------
        image : :class:`Attachment`
            The image to dump.
            
        Returns:
        --------
        :class:`str`
            The URL of the dumped image.
        """
        
        file = await image.to_file()
        post = await self._img_dump.send(file=file)   # type: ignore

        return post.attachments[0].url

################################################################################
    async def report_error(self, ctx: ApplicationContext, error: DiscordException) -> None:

        if os.getenv("DEBUG") == "True":
            print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
            return

        tb_list = traceback.format_exception(type(error), error, error.__traceback__)

        tz = pytz.timezone("America/Los_Angeles")
        try:
            directory = "ErrorLogs/"
            fp = f"ErrorLogs/{tz.localize(datetime.now()).strftime('%m-%d-%y-%H-%M-%S')}-error.log"
            os.makedirs(directory, exist_ok=True)
            with open(fp, "w") as file:
                file.write("".join(tb_list))
                log.info(None, f"Error logged to {fp}")
        except OSError as e:
            log.error(None, f"Error logging to {fp}: {e.args}")

        divider = "The above exception was the direct cause of the following exception:"
        divider_loc = None
        for i, line in enumerate(tb_list):
            if divider in line:
                divider_loc = i
                break

        if divider_loc is not None:
            tb_list = tb_list[:divider_loc]

        tb_str = "\n".join(tb_list)

        if len(tb_str) > 4000:
            tb_str = tb_str[:4000] + '...'

        await self._error_dump.send(
            f"# __Error in Command:__ `{ctx.command.name}`\n```{tb_str}```",
            file=File(fp)
        )

################################################################################
    async def help(self, interaction: Interaction) -> None:

        embed = U.make_embed(
            title="FroggeBot Help",
            description=(
                "FroggeBot is a Discord application designed to help manage and facilitate "
                "FFXIV role-playing venue events, activities, and management.\n\n"
                
                "For more detailed information, visit the [Online Documentation]"
                "(https://allegrovivo.github.io/FroggeDocs/).\n\n"
                
                "Or you can visit our [Discord Server](https://discord.gg/CxQNuYVFK3)!\n\n"
            ),
            color=int("4ABC23", 16),
            thumbnail_url=BotImages.ThumbsUpFrog
        )
        await interaction.respond(embed=embed, ephemeral=True)

################################################################################
