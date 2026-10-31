import discord
from discord.ext import commands
import datetime
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.global_models import GlobalUser

class RewardsModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="daily", help="Claim your daily Lunas reward.")
    async def daily(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(GlobalUser).where(GlobalUser.user_id == ctx.author.id))
            user = res.scalar_one_or_none()
            if not user:
                user = GlobalUser(user_id=ctx.author.id)
                session.add(user)

            if user.last_daily and (now - user.last_daily).total_seconds() < 86400:
                rem = 86400 - int((now - user.last_daily).total_seconds())
                await ctx.send(f"⏳ Daily reward available in **{rem // 3600}h {(rem % 3600) // 60}m**.")
                return

            reward = 250
            user.lunas += reward
            user.last_daily = now
            await session.commit()

            embed = discord.Embed(title="🎁 Daily Reward", description=f"You claimed **+{reward} Lunas**!", color=0x4B0082)
            await ctx.send(embed=embed)

    @commands.command(name="weekly", help="Claim your weekly Lunas reward.")
    async def weekly(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(GlobalUser).where(GlobalUser.user_id == ctx.author.id))
            user = res.scalar_one_or_none()
            if not user:
                user = GlobalUser(user_id=ctx.author.id)
                session.add(user)

            # Sunday 00:00 UTC calculation check
            if user.last_weekly:
                days_since = (now - user.last_weekly).days
                if days_since < 7:
                    await ctx.send("⏳ You have already claimed your weekly reward for this cycle.")
                    return

            reward = 1500
            user.lunas += reward
            user.last_weekly = now
            await session.commit()

            embed = discord.Embed(title="👑 Weekly Reward", description=f"You claimed **+{reward} Lunas**!", color=0x8B0000)
            await ctx.send(embed=embed)

    @commands.command(name="monthly", help="Claim your monthly Lunas reward.")
    async def monthly(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(GlobalUser).where(GlobalUser.user_id == ctx.author.id))
            user = res.scalar_one_or_none()
            if not user:
                user = GlobalUser(user_id=ctx.author.id)
                session.add(user)

            if user.last_monthly and (now - user.last_monthly).days < 30:
                await ctx.send("⏳ You have already claimed your monthly reward for this period.")
                return

            reward = 5000
            user.lunas += reward
            user.last_monthly = now
            await session.commit()

            embed = discord.Embed(title="🍷 Monthly Reward", description=f"You claimed **+{reward} Lunas**!", color=0x4B0082)
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RewardsModule(bot))
