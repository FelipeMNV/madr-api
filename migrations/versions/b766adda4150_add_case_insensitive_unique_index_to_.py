"""add case insensitive unique index to romancistas

Revision ID: b766adda4150
Revises: 7bd1cd3dd5c5
Create Date: 2026-11-03 16:55:31.030078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b766adda4150'
down_revision: Union[str, Sequence[str], None] = '7bd1cd3dd5c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'uq_romancistas_nome_lower',
        'romancistas',
        [sa.text('lower(nome)')],
        unique=True,
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'uq_romancistas_nome_lower',
        table_name='romancistas',
    )
