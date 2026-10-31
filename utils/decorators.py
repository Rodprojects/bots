import discord
from discord.ext import commands
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.guild_models import GuildConfig

async def is_night_admin(ctx: commands.Context) -> bool:
    """
    Checks if the command invoker is the Server Owner, holds Discord Administrator permissions,
    or possesses the server-specific admin role configured in the persistent volume database.
    """
    if not ctx.guild:
        return False

    # 1. Server Owner always has permission
    if ctx.author.id == ctx.guild.owner_id:
        return True

    # 2. Server Discord Administrators always have permission
    if ctx.author.guild_permissions.administrator:
        return True

    # 3. Query persistent database for custom admin role configured via !setadminrole
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(GuildConfig).where(GuildConfig.guild_id == ctx.guild.id))
        guild_cfg = result.scalar_one_or_none()

        if guild_cfg and guild_cfg.admin_role_id:
            admin_role = ctx.guild.get_role(guild_cfg.admin_role_id)
            if admin_role and admin_role in ctx.author.roles:
                return True

    return False

def has_night_admin_permission():
    """Custom command decorator to enforce Night admin checks on management commands."""
    async def predicate(ctx: commands.Context):
        if await is_night_admin(ctx):
            return True
        await ctx.send("❌ *Access denied. You lack the designated Night Admin authority in this realm.*")
        return False
    return commands.check(predicate)
