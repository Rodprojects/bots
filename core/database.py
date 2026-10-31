import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import config
from core.logger import logger
from database.global_models import Base
from database.guild_models import GuildConfig  # Register guild models

# Ensure the parent directory for the SQLite file exists on your volume
if "sqlite" in config.DATABASE_URL:
    db_path = config.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    if "/" in db_path:
        dir_name = os.path.dirname(db_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

# Initialize Async Engine for SQLite on Volume
engine = create_async_engine(
    config.DATABASE_URL,
    echo=config.DEBUG_MODE,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initializes database connection pool, creates tables, and verifies connectivity."""
    try:
        async with engine.begin() as conn:
            # Automatically create all tables (Global & Guild models)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("🔥 Secure SQLite connection established on your Railway volume. Tables synchronized.")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_db():
    """Gracefully closes database connections on shutdown."""
    await engine.dispose()
    logger.info("💤 Database connection pool closed gracefully.")
