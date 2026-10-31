from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class GlobalUser(Base):
    __tablename__ = "global_users"

    user_id = Column(BigInteger, primary_key=True, index=True)
    lunas = Column(Integer, default=100)  # Starting bonus for entering the Red Room
    last_daily = Column(DateTime, nullable=True)

    # Relationship to user's global inventory
    inventory = relationship("GlobalInventory", back_populates="user", cascade="all, delete-orphan")

class GlobalInventory(Base):
    __tablename__ = "global_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("global_users.user_id"), nullable=False)
    item_name = Column(String, nullable=False)
    item_type = Column(String, default="cosmetic")
    acquired_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("GlobalUser", back_populates="inventory")
