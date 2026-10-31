import asyncio
import importlib
import inspect
import os
import sys
import discord
from discord.ext import commands

from core.config import config
from core.logger import logger
from core.database import init_db, close_db

class RedRoomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        logger.info("🍷 Initiating Red-Room Ecosystem Core Sequences...")
        
        # 1. Initialize Database
        await init_db()

        # 2. Load all modules dynamically from the flat 'modules/' directory
        await self.load_all_modules()

        # 3. Register Persistent Views (Prevents 'Interaction Failed' errors on restart)
        await self.register_persistent_views()

        logger.info("✨ All core systems synchronized and fully operational.")

    async def load_all_modules(self):
        """Dynamically imports and loads all python modules from the modules/ directory."""
        modules_dir = "modules"
        if not os.path.exists(modules_dir):
            os.makedirs(modules_dir)
            logger.warning(f"⚠️ Directory '{modules_dir}' was missing and has been created.")

        loaded_count = 0
        for filename in os.listdir(modules_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    # Import module dynamically
                    mod = importlib.import_module(f"modules.{module_name}")
                    
                    # If the module has a setup function (standard discord.py extension style), call it
                    if hasattr(mod, "setup"):
                        if inspect.iscoroutinefunction(mod.setup):
                            await mod.setup(self)
                        else:
                            mod.setup(self)
                        logger.info(f"📂 Loaded module extension: {module_name}")
                    else:
                        logger.info(f"📂 Loaded module script: {module_name}")
                    
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to load module '{module_name}': {e}")

        logger.info(f"🚀 Successfully loaded {loaded_count} modules from '{modules_dir}/'.")

    async def register_persistent_views(self):
        """
        Re-attaches persistent views/buttons from database records on startup 
        so buttons never trigger 'Interaction Failed' after restarts.
         """
        logger.info("🔒 Registering persistent interaction views...")
        try:
            # We will query our persistent views module/registry once implemented
            if "modules.persistent_views" in sys.modules:
                persistent_module = sys.modules["modules.persistent_views"]
                if hasattr(persistent_module, "register_views"):
                    await persistent_module.register_views(self)
                    logger.info("🛡️ Persistent interaction views successfully re-anchored.")
            else:
                logger.info("🛡️ No active persistent views registry detected yet. Skipping initial re-anchoring.")
        except Exception as e:
            logger.error(f"⚠️ Error while re-anchoring persistent views: {e}")

    async def on_ready(self):
        logger.info(f"🌹 Connected as {self.user} (ID: {self.user.id}) — The Red Room is open.")

async def main():
    # Validate environment configuration before starting
    config.validate()

    bot = RedRoomBot()

    try:
        async with bot:
            await bot.start(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down gracefully by Master's command...")
    finally:
        await close_db()
        logger.info("🌙 Ecosystem offline. Sweet nightmares.")

if __name__ == "__main__":
    asyncio.run(main())
