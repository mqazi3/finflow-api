"""add transaction description and account foreign key

Revision ID: b7c2e4f19a3d
Revises: af1db66db39e
Create Date: 2026-09-28 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c2e4f19a3d'
down_revision: Union[str, Sequence[str], None] = 'af1db66db39e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('transactions', sa.Column('description', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_transactions_account_id_accounts',
        'transactions',
        'accounts',
        ['account_id'],
        ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_transactions_account_id_accounts', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'description')
