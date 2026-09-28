from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.database import Base, utc_now


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Numeric(12, 2), default=0)

    created_at = Column(DateTime, default=utc_now)