from sqlalchemy.orm import Session

from app.models.account import Account


def create_account(db: Session, account_data, user_id: int):
    account = Account(
        user_id=user_id,
        name=account_data.name,
        account_type=account_data.account_type,
        balance=account_data.balance
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


def get_accounts(db: Session, user_id: int):
    return db.query(Account).filter(Account.user_id == user_id).all()