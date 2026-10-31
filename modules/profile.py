import discord
from discord.ext import commands
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.global_models import GlobalUser

class ProfileModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="profile", aliases=["perfil", "stats"], help="Displays your global profile and stats.")
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(GlobalUser).where(GlobalUser.user_id == target.id))
            user = result.scalar_one_or_none()

            if not user:
                user = GlobalUser(user_id=target.id, lunas=100)
                session.add(user)
                await session.commit()
                await session.refresh(user)

            embed = discord.Embed(
                title=f"🌹 Profile — {target.display_name}",
                description=f"Global statistics and record for {target.mention}",
                color=0x8B0000
            )
            embed.set_thumbnail(url=target.display_avatar.url)

            # Economic & Engagement Overview
            embed.add_field(name="💰 Currency", value=f"**{user.lunas:,} Lunas**", inline=True)
            embed.add_field(name="📝 Server Activity", value=f"**{user.posts_count:,} Messages**", inline=True)
            embed.add_field(name="🎲 Games (W/L)", value=f"**{user.games_won:,}** / **{user.games_played:,}**", inline=True)

            # Roleplay & Interactions Count
            embed.add_field(name="🔥 Actions Dealt", value=f"**{user.actions_given:,}**", inline=True)
            embed.add_field(name="⛓️ Actions Received", value=f"**{user.actions_received:,}**", inline=True)

            embed.set_footer(text="Night Ecosystem — Profile Record")
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileModule(bot))
