from __future__ import annotations

import os

from discord import Intents
from dotenv import load_dotenv

from Classes.Core.Bot import FroggeBot
################################################################################

load_dotenv()
DEBUG = os.getenv("DEBUG")

################################################################################

debug_guilds = None
if DEBUG == "True":
    debug_guilds = [
        955933227372122173,  # Bot Resources
        1273061765831458866,  # Kupo Nutz
    ]

bot = FroggeBot(
    description="Ribbit ribbit!",
    intents=Intents.all(),
    debug_guilds=debug_guilds
)

################################################################################

for filename in os.listdir("Cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"Cogs.{filename[:-3]}")

################################################################################

token = os.getenv(("DEBUG" if DEBUG == "True" else "DISCORD") + "_TOKEN")
bot.run(token)

################################################################################
