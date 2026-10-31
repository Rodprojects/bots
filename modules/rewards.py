import discord
from discord.ext import commands
import datetime
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.global_models import GlobalUser

class RewardsModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_or_create_user(self, session, user_id: int) -> GlobalUser:
        res = await session.execute(select(GlobalUser).where(GlobalUser.user_id == user_id))
        user = res.scalar_one_or_none()
        if not user:
            user = GlobalUser(user_id=user_id, lunas=100)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        if user.lunas is None:
            user.lunas = 100
        return user

    @commands.command(name="daily", help="Claim your daily Lunas reward.")
    async def daily(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        async with AsyncSessionLocal() as session:
            user = await self.get_or_create_user(session, ctx.author.id)

            if user.last_daily and (now - user.last_daily).total_seconds() < 86400:
                rem = 86400 - int((now - user.last_daily).total_seconds())
                await ctx.send(f"⏳ Daily reward available in **{rem // 3600}h {(rem % 3600) // 60}m**.")
                return

            reward = 250
            user.lunas += reward
            user.last_daily = now
            await session.commit()

            embed = discord.Embed(title="🎁 Daily Reward", description=f"You claimed **+{reward} Lunas**!\nYour vault holds **{user.lunas:,} Lunas**.", color=0x4B0082)
            await ctx.send(embed=embed)

    @commands.command(name="weekly", help="Claim your weekly Lunas reward.")
    async def weekly(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        async with AsyncSessionLocal() as session:
            user = await self.get_or_create_user(session, ctx.author.id)

            if user.last_weekly and (now - user.last_weekly).total_seconds() < 604800:
                rem = 604800 - int((now - user.last_weekly).total_seconds())
                days = rem // 86400
                hours = (rem % 86400) // 3600
                await ctx.send(f"⏳ Weekly reward available in **{days}d {hours}h**.")
                return

            reward = 1500
            user.lunas += reward
            user.last_weekly = now
            await session.commit()

            embed = discord.Embed(title="👑 Weekly Reward", description=f"You claimed **+{reward} Lunas**!\nYour vault holds **{user.lunas:,} Lunas**.", color=0x8B0000)
            await ctx.send(embed=embed)

    @commands.command(name="monthly", help="Claim your monthly Lunas reward.")
    async def monthly(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        async with AsyncSessionLocal() as session:
            user = await self.get_or_create_user(session, ctx.author.id)

            if user.last_monthly and (now - user.last_monthly).total_seconds() < 2592000:
                rem = 2592000 - int((now - user.last_monthly).total_seconds())
                days = rem // 86400
                await ctx.send(f"⏳ Monthly reward available in **{days} days**.")
                return

            reward = 5000
            user.lunas += reward
            user.last_monthly = now
            await session.commit()

            embed = discord.Embed(title="🍷 Monthly Reward", description=f"You claimed **+{reward} Lunas**!\nYour vault holds **{user.lunas:,} Lunas**.", color=0x4B0082)
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RewardsModule(bot))
