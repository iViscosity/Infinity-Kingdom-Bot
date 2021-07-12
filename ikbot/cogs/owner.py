import json
import os
from datetime import datetime, timezone
from pathlib import Path

import discord
import util
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, *, cog: str):
        """Reloads a cog module"""

        try:
            self.bot.unload_extension(f'cogs.{cog}')
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, *, cog: str):
        """Loads an unloaded cog module"""

        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, *, cog: str):
        """Unloads a loaded cog module"""

        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='prefix', aliases=['setprefix'])
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, new_prefix: str):
        await util.save_setting(ctx.guild.id, new_prefix)
        await ctx.send(f'Successfully changed prefix to {new_prefix}!')
        await ctx.bot.change_presence(activity=discord.Game('Infinity Kingdom'))

    @commands.command(name='setup', aliases=['timer', 'createtimer'])
    @commands.has_permissions(administrator=True)
    async def setup_timers(self, ctx, overwrite: str = None):
        '''Creates voice channels to track UTC time and date.'''

        old_category = await util.load_setting(ctx.guild.id, 'time_category')
        old_date = await util.load_setting(ctx.guild.id, 'date_channel')
        old_time = await util.load_setting(ctx.guild.id, 'time_channel')

        if old_category:
            old_category = ctx.bot.get_channel(old_category)

        if old_date:
            old_date = ctx.bot.get_channel(old_date)

        if old_time:
            old_time = ctx.bot.get_channel(old_time)

        if old_category is not None and overwrite != 'FORCE':
            return await ctx.send('A category already exists. Please reuse this command using "FORCE" to recreate them: **`$setup FORCE`**')

        if old_category and overwrite == 'FORCE':
            if old_date:
                await old_date.delete()

            if old_time:
                await old_time.delete()

            if old_category:
                await old_category.delete()

        category_name = '⬩⬥❯❯ GAME TIME ❮❮⬥⬩'
        date_channel_format = 'Date: %s'
        time_channel_format = 'Time: %s UTC'

        _overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False)
        }

        now = datetime.now(timezone.utc)
        category = await ctx.guild.create_category(
            category_name, position=0, overwrites=_overwrites)
        date_channel = await category.create_voice_channel(
            date_channel_format % (now.strftime('%d %b')))
        time_channel = await category.create_voice_channel(
            time_channel_format % (now.strftime('%H:%M')))

        await util.save_setting(ctx.guild.id, 'time_category', category.id)
        await util.save_setting(ctx.guild.id, 'date_channel', date_channel.id)
        await util.save_setting(ctx.guild.id, 'time_channel', time_channel.id)


def setup(bot):
    bot.add_cog(Owner(bot))
