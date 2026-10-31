import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import config
from core.logger import logger

# Initialize Async Engine for PostgreSQL
engine = create_async_engine(
    config.DATABASE_URL,
    echo=config.DEBUG_MODE,
    pool_pre_ping=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initializes database connection pool and verifies connectivity."""
    try:
        async with engine.begin() as conn:
            logger.info("🔥 Secure database connection established. PostgreSQL heartbeat pulsing.")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

async def close_db():
    """Gracefully closes database connections on shutdown."""
    await engine.dispose()
    logger.info("💤 Database connection pool closed gracefully.")
