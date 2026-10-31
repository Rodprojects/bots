import discord
from discord.ext import commands
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.guild_models import GuildConfig

class ServerManagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="setadminrole", help="Sets the designated administrator role for Night commands in this server.")
    async def set_admin_role(self, ctx: commands.Context, role: discord.Role):
        # Only server owner or users with Administrator permission can execute this
        if not (ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator):
            await ctx.send("❌ *Only the Server Owner or an Administrator can designate Night's admin role.*")
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(GuildConfig).where(GuildConfig.guild_id == ctx.guild.id))
            guild_cfg = result.scalar_one_or_none()

            if not guild_cfg:
                guild_cfg = GuildConfig(guild_id=ctx.guild.id, admin_role_id=role.id)
                session.add(guild_cfg)
            else:
                guild_cfg.admin_role_id = role.id

            await session.commit()

        embed = discord.Embed(
            title="⚙️ Administration Role Configured",
            description=f"The role {role.mention} has been bound as Night's administrative authority for **{ctx.guild.name}**.",
            color=0x4B0082
        )
        embed.set_footer(text="Server-Specific Configuration")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerManagement(bot))
