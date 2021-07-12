import asyncio
import json
import os
from pathlib import Path

import discord
from discord.ext import commands

import util

'''
This is an AIO Discord bot for the mobile game Infinity Kingdom.

Written in Python 3.

Copyright 2021 Spencer Murphy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

SETTINGS_PATH = os.path.join(Path().absolute(), f'settings/')
DEFAULT_PREFIX = '$'


async def get_prefix_for(guild):
    '''Searches the saved files for this guild and tries to get it's prefix'''

    path = os.path.join(SETTINGS_PATH, f'guilds/{guild}.json')
    if not os.path.isfile(path):
        await util.save_setting(guild, 'prefix', DEFAULT_PREFIX)

    with open(path) as f:
        return json.load(f)['prefix']


async def get_prefix(bot, message):
    '''Gets the prefix for the bot.'''

    prefix = DEFAULT_PREFIX
    bot.current_guild = message.guild.id
    current_prefix = await get_prefix_for(bot.current_guild)

    if current_prefix is not None and current_prefix != DEFAULT_PREFIX:
        prefix = current_prefix

    # Allows us to @mention the bot or use the prefix
    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(command_prefix=get_prefix,
                   description='An AIO Infinity Kingdom Discord bot')

modules = [
    'cogs.user',
    'cogs.admin',
    'cogs.owner',
    'cogs.events',
]


@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user.name} : {bot.user.id}!')

    print(f'Setting presence...', end='')
    await bot.change_presence(activity=discord.Game('Infinity Kingdom'))
    print('done!')

    print(f'Verifying immortal data...', end='')
    err_count = 0
    immortal_count = 0

    for file_name in [x[0] for x in os.walk('.\\immortal_data')][1:]:
        immortal_name = file_name.split('\\')[2]
        
        with open(os.path.join(Path().absolute(), 'immortal_data', immortal_name, 'info.json')) as f:
            try:
                json.load(f)
                immortal_count += 1
            except ValueError as e:
                err_count += 1
                print(f'JSON parse error in {immortal_name} : {e}')

    print(f'done! Immortals loaded: {immortal_count}. Errors found: {err_count}')

if __name__ == '__main__':
    for module in modules:
        bot.load_extension(module)

    bot.run(os.environ.get('BOT_TOKEN'))
