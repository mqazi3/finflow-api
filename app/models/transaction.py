from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    account_id = Column(Integer, index=True)
    amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=False)
    category = Column(String, nullable=False)

    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)