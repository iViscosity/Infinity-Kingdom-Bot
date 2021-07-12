import difflib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import process_time

import discord
from discord.ext import commands

# Global lookup constants
BASE_PATH = Path().absolute()
SUPPORTED_IMMORTALS = sorted(os.listdir(os.path.join(BASE_PATH, 'immortal_data')))

class User(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member=None):
        """Tells when a member joined. Defaults to author."""

        if member is None:
            member = ctx.author

        await ctx.send(f'{member.display_name} joined on {member.joined_at}')

    @commands.command()
    async def ping(self, ctx):
        """Responds with the bot ping time"""

        start = ctx.message.created_at
        end = datetime.now(timezone.utc)
        
        await ctx.send(f'Pong! (took {(end - start).total_seconds()}s)')

    @commands.command(aliases=['immortalinfo', 'immortal', 'info'], description='Looks up information about an Immortal')
    async def immortal_info(self, ctx, *, immortal_name: str = ""):
        """Looks up information about a certain immortal.

        Can be one of the following:

            1. Exact match (e.g. Merlin)
            2. Substring of full immortal name (e.g. Alexander -> Alexander the Great)
            3. Similar name lookup (will show closest 3 matches)

        Currently only supports English name, plans to add localization later.
        """

        if immortal_name == "":
            builder = 'Supported immortals:\n```'

            for i in SUPPORTED_IMMORTALS:
                f = open(os.path.join(BASE_PATH, f'immortal_data/{i}/info.json'))
                data = json.load(f)

                builder += data[i]['Name'] + '\n'

            builder += '```'
            await ctx.send(builder)
            return

        original_message = ctx.message

        immortal_name = immortal_name.lower().replace(' ', '-')
        match = None

        # If it's an exact match
        if immortal_name in SUPPORTED_IMMORTALS:
            match = immortal_name

        # Check for substring
        if not match:
            try:
                match = next((immortal for immortal in SUPPORTED_IMMORTALS if immortal_name in immortal))
            except StopIteration:
                pass

        if not match:
            matches = difflib.get_close_matches(immortal_name, SUPPORTED_IMMORTALS, cutoff=0.3)
            num_matches = len(matches)

            print(f'Specified input: {immortal_name}. Found {num_matches} match(es): {matches}')

            # Create embed
            embed = discord.Embed(color=0x8B008B, title='Immortal Information', description='Please select the correct immortal')
            embed.set_footer(text='IK Bot - Physh')
            embed.timestamp = datetime.utcnow()

            # Add options found earlier (if any)
            if num_matches == 0:
                embed.description = 'No immortals found!'
                embed.add_field(name='Error', value=f'Could not find any immortal matching the name \'{immortal_name}\'. Please try again...')
                await ctx.send(embed)
                return
            else:
                if num_matches >= 1:
                    f = open(os.path.join(BASE_PATH, f'immortal_data/{matches[0]}/info.json'))
                    data = json.load(f)

                    embed.add_field(name='Option 1', value=data[matches[0]]['Name'])

                if num_matches >= 2:
                    f = open(os.path.join(BASE_PATH, f'immortal_data/{matches[1]}/info.json'))
                    data = json.load(f)

                    embed.add_field(name='Option 2', value=data[matches[1]]['Name'])

                if num_matches == 3:
                    f = open(os.path.join(BASE_PATH, f'immortal_data/{matches[2]}/info.json'))
                    data = json.load(f)

                    embed.add_field(name='Option 3', value=data[matches[2]]['Name'])

            # Send the message and save the var
            message = await ctx.send(embed=embed)

            # Add reactions
            if num_matches >= 1:
                await message.add_reaction('1️⃣')

            if num_matches >= 2:
                await message.add_reaction('2️⃣')

            if num_matches == 3:
                await message.add_reaction('3️⃣')

            await message.add_reaction('❌')

            # Custom check to see if they reacted to our message and with what.
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == message.id and (str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣' or str(reaction.emoji) == '❌')

            # Get the reaction
            reaction, user = await ctx.bot.wait_for('reaction_add', check=check)

            # Prevent clutter
            await message.delete()

            # Check for reaction
            if str(reaction.emoji) == '1️⃣':
                match = matches[0]
            elif str(reaction.emoji) == '2️⃣':
                match = matches[1]
            elif str(reaction.emoji) == '3️⃣':
                match = matches[2]
            elif str(reaction.emoji) == '❌':
                builder = 'Could not find the Immortal! Supported immortals:\n```\n'
                for i in SUPPORTED_IMMORTALS:
                    f = open(os.path.join(BASE_PATH, f'immortal_data/{i}/info.json'))
                    data = json.load(f)

                    builder += data[i]['Name'] + '\n'

                builder += '```'
                await ctx.send(builder)
                return

            #print(data)

        # Reopen the immortal data for the match
        path = os.path.join(BASE_PATH, f'immortal_data/{match}/')
        f = open(path + 'info.json')
        data = json.load(f)[match]

        # Start embed
        embed = discord.Embed(color=0xFFD700, title=data['Name'], description=data['Description'])
        try:
            # Open the image if there is one
            image = discord.File(path + 'sprite.png', filename=f'{match}.png')
            embed.set_image(url=f'attachment://{match}.png')
        except FileNotFoundError:
            image = None

        embed.set_footer(text='IK Bot - Physh')
        embed.timestamp = datetime.utcnow()

        embed.add_field(name='Troop Type', value=data['Troop Type'], inline=False)
        embed.add_field(name='Element', value=data['Element'], inline=False)
        embed.add_field(name='Position', value=data['Position'], inline=False)

        embed.add_field(name='Attributes', value=f'Strength: {data["Attributes"]["Strength"]}\nAgility: {data["Attributes"]["Agility"]}\nIntelligence: {data["Attributes"]["Intelligence"]}\nPhysique: {data["Attributes"]["Physique"]}\nAptitude: {data["Attributes"]["Aptitude"]}\nEnergy Regen.: {data["Attributes"]["Energy Regen."]}', inline=False)

        embed.add_field(name='Active Skill', value=f'Name: {data["Active Skill"]["Name"]}\nDescription: {data["Active Skill"]["Description"]}', inline=False)

        if image:
            await ctx.send(file=image, embed=embed)
        else:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(User(bot))
