"""add audit timestamps

Revision ID: 967b3f6f02f3
Revises: 285c86e13beb
Create Date: 2026-09-26 01:54:46.041672

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ============================================================
# REVISION IDENTIFIERS
# ============================================================

revision: str = "967b3f6f02f3"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "285c86e13beb"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:

    # --------------------------------------------------------
    # ACCESS EVENTS
    # --------------------------------------------------------

    op.add_column(
        "access_events",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "access_events",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


    # --------------------------------------------------------
    # PERMISSIONS
    # --------------------------------------------------------

    op.add_column(
        "permissions",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:

    op.drop_column(
        "permissions",
        "updated_at"
    )

    op.drop_column(
        "access_events",
        "updated_at"
    )

    op.drop_column(
        "access_events",
        "created_at"
    )