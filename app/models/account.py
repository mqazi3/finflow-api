from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)