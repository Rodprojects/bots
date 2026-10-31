from sqlalchemy import Column, BigInteger
from database.global_models import Base

class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id = Column(BigInteger, primary_key=True, index=True)
    admin_role_id = Column(BigInteger, nullable=True)
