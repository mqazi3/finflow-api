"""store money as numeric(12, 2) and require transaction account

Revision ID: c4d8a1e6b2f7
Revises: b7c2e4f19a3d
Create Date: 2026-09-28 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d8a1e6b2f7'
down_revision: Union[str, Sequence[str], None] = 'b7c2e4f19a3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Existing float values are rounded to the nearest cent
    op.alter_column(
        'transactions',
        'amount',
        type_=sa.Numeric(12, 2),
        existing_type=sa.Float(),
        existing_nullable=False,
        postgresql_using='round(amount::numeric, 2)',
    )
    op.alter_column(
        'accounts',
        'balance',
        type_=sa.Numeric(12, 2),
        existing_type=sa.Float(),
        existing_nullable=True,
        postgresql_using='round(balance::numeric, 2)',
    )
    # Every transaction belongs to an account. This fails if any existing row
    # has no account; such rows would need to be fixed or removed first.
    op.alter_column(
        'transactions',
        'account_id',
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'transactions',
        'account_id',
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        'accounts',
        'balance',
        type_=sa.Float(),
        existing_type=sa.Numeric(12, 2),
        existing_nullable=True,
    )
    op.alter_column(
        'transactions',
        'amount',
        type_=sa.Float(),
        existing_type=sa.Numeric(12, 2),
        existing_nullable=False,
    )
