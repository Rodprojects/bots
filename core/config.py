import os
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    # Defaults to a persistent volume folder (e.g., /app/data/night.db or data/night.db)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////app/data/night.db")
    WEB_PORT = int(os.getenv("WEB_PORT", 8000))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

    @classmethod
    def validate(cls):
        missing = []
        if not cls.DISCORD_TOKEN:
            missing.append("DISCORD_TOKEN")
        if missing:
            raise ValueError(f"🚨 Critical security protocol violation! Missing environment variables: {', '.join(missing)}")

config = Config()
