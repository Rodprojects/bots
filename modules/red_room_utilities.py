import discord
from discord.ext import commands

class RedRoomUtilities:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping", help="Tests Night's pulse and connection latency.")
    async def ping(self, ctx: commands.Context):
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        # Crafting the dark luxury embed
        embed = discord.Embed(
            title="🍷 Heartbeat Check",
            description=f"My pulse is currently beating at **{latency}ms**.\n*Care to test how much load I can handle, Master?*",
            color=0x8B0000  # Deep Blood Red
        )
        embed.set_footer(text="Night Ecosystem — Always listening, always ready.")
        
        await ctx.send(embed=embed)

    @commands.command(name="night", help="Displays information about the Night ecosystem.")
    async def night_info(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🌹 The Red Room Awaits",
            description=(
                "I am **Night**—your exclusive, highly polished, and seductive digital companion. "
                "Running smoothly on secure volumes and private databases, built to command your community with absolute elegance."
            ),
            color=0x4B0082  # Luxurious Indigo/Purple
        )
        embed.add_field(
            name="🔒 Status", 
            value="Encrypted, persistent, and entirely under your control.", 
            inline=False
        )
        embed.set_footer(text="Designed for absolute dominance.")
        
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RedRoomUtilities(bot))
