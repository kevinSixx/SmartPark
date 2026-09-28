"""add face profiles and samples

Revision ID: 0945aa4d18a8
Revises: 967b3f6f02f3
Create Date: 2026-09-26 14:52:21.219290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0945aa4d18a8'
down_revision: Union[str, Sequence[str], None] = '967b3f6f02f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
