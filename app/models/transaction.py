from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String

from app.database import Base, utc_now


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    account_id = Column(Integer, ForeignKey("accounts.id"), index=True, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    merchant = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)

    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
