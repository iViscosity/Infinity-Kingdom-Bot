import re
from typing import Union

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member = None, role: Union[str, discord.Member] = None, *, reason: str = 'no reason given'):
        """Sets a user's role"""

        if role is None:
            return await ctx.send('Please specify a role!')

        role_id = re.search(r'\d{18}', role)

        if role_id is not None:
            role_id = int(role_id.group(0))
            role = discord.utils.get(ctx.guild.roles, id=role_id)
        else:
            if isinstance(role, str):
                role = discord.utils.get(ctx.guild.roles, name=role)
            elif role is None:
                await ctx.send("Please specify a role.")
                return

        if not isinstance(role, discord.Role):
            await ctx.send('Role could not be found.')
            return

        if member is None or not isinstance(member, discord.Member):
            await ctx.send('Please @mention a valid member.')
            return

        add = discord.utils.get(ctx.author.roles, id=role.id) is None

        try:
            if add:
                await member.add_roles(role, reason=reason)
            else:
                await member.remove_roles(role, reason=reason)
        except discord.Forbidden:
            await ctx.send('I don\'t have permission to add or remove this role. Make sure I have the "Manage Roles" permission and this role is not above my highest role.')
        except discord.HTTPException as e:
            await ctx.send(f'Something went wrong adding or removing this role: {e}')
        else:
            await ctx.send(f'Successfully {("added" if add else "removed")} {member.display_name} {("to" if add else "from")} {role}!')


def setup(bot):
    bot.add_cog(Admin(bot))
