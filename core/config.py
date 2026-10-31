import os
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/night_db")
    WEB_PORT = int(os.getenv("WEB_PORT", 8000))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

    @classmethod
    def validate(cls):
        missing = []
        if not cls.DISCORD_TOKEN:
            missing.append("DISCORD_TOKEN")
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
        if missing:
            raise ValueError(f"🚨 Critical security protocol violation! Missing environment variables: {', '.join(missing)}")

config = Config()
