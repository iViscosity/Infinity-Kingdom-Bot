import json
import os
from pathlib import Path

import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open(self.settings_path) as f:
            guild_info = json.load(f)

        guild_info[guild.id] = {}

        with open(self.settings_path) as f:
            json.dump(guild_info, f)


def setup(bot):
    bot.add_cog(Events(bot))
