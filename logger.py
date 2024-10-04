from __future__ import annotations

import logging
import sys
from logging import Formatter, FileHandler, StreamHandler
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################
class FullDataFormatter(Formatter):

    def __init__(self):

        super().__init__(
            fmt=(
                "%(asctime)s - %(name)10s::%(levelname)-8s - %(message)s"
            ),
            datefmt="%m/%d/%y %H:%M:%S"
        )

################################################################################
class StreamDataFormatter(Formatter):

    def __init__(self):

        super().__init__(
            fmt="%(asctime)s - %(name)s::%(levelname)s - %(message)s",
            datefmt="%m/%d/%y %H:%M:%S"
        )

################################################################################
class _FroggeLog:

    _FDF = FullDataFormatter()
    _SDF = StreamDataFormatter()

    _FH = FileHandler("log.log", "w", encoding='utf-8')
    _SH = StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))

################################################################################
    def __init__(self):
        
        self._FH.setLevel(logging.DEBUG)
        self._FH.setFormatter(self._FDF)
        # self._SH.setLevel(logging.WARNING)
        self._SH.setLevel(logging.DEBUG)
        self._SH.setFormatter(self._SDF)
    
################################################################################    
    def _log(self, guild: Optional[GuildData], level: int, message: str) -> None:

        logger = logging.getLogger(guild.parent.name if guild else "FroggeBot-Core")
        logger.setLevel(level)
        logger.addHandler(self._FH)
        logger.addHandler(self._SH)
        
        try:
            logger.log(level, message, exc_info=level >= logging.CRITICAL)
        except Exception as e:
            print(e)
    
################################################################################
    def debug(self, guild: Optional[GuildData], message: str) -> None:
        
        self._log(guild, logging.DEBUG, message)
        
################################################################################
    def info(self, guild: Optional[GuildData], message: str) -> None:
        
        self._log(guild, logging.INFO, message)
        
################################################################################
    def warning(self, guild: Optional[GuildData], message: str) -> None:
        
        self._log(guild, logging.WARNING, message)
        
################################################################################
    def error(self, guild: Optional[GuildData], message: str) -> None:
        
        self._log(guild, logging.ERROR, message)
        
################################################################################
    def critical(self, guild: Optional[GuildData], message: str) -> None:
        
        self._log(guild, logging.CRITICAL, message)
        
################################################################################

log = _FroggeLog()

################################################################################
