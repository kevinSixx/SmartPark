"""add staff accounts and gate actions

Revision ID: 7f2c9d1a4b6e
Revises: 8e1b0efdf278
Create Date: 2026-09-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f2c9d1a4b6e"
down_revision: Union[str, None] = "8e1b0efdf278"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ========================================================
    # STAFF ACCOUNTS
    # ========================================================

    op.create_table(
        "staff_accounts",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "full_name",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "username",
            sa.String(length=80),
            nullable=False,
        ),

        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.CheckConstraint(
            "role IN ('ADMIN', 'GUARD')",
            name="ck_staff_accounts_role",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "username"
        ),
    )

    op.create_index(
        "ix_staff_accounts_username",
        "staff_accounts",
        ["username"],
        unique=False,
    )

    op.create_index(
        "ix_staff_accounts_role",
        "staff_accounts",
        ["role"],
        unique=False,
    )


    # ========================================================
    # GATE ACTIONS
    # ========================================================

    op.create_table(
        "gate_actions",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "gate_id",
            sa.String(length=50),
            server_default="gate-01",
            nullable=False,
        ),

        sa.Column(
            "action",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "source",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "staff_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "access_event_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "reason",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "observation",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=20),
            server_default="SUCCESS",
            nullable=False,
        ),

        sa.Column(
            "error_message",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.CheckConstraint(
            "action IN ('OPEN', 'CLOSE')",
            name="ck_gate_actions_action",
        ),

        sa.CheckConstraint(
            "source IN ('AUTO', 'MANUAL')",
            name="ck_gate_actions_source",
        ),

        sa.CheckConstraint(
            "status IN ('SUCCESS', 'ERROR')",
            name="ck_gate_actions_status",
        ),

        sa.ForeignKeyConstraint(
            ["staff_id"],
            ["staff_accounts.id"],
            ondelete="SET NULL",
        ),

        sa.ForeignKeyConstraint(
            ["access_event_id"],
            ["access_events.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_gate_actions_timestamp",
        "gate_actions",
        ["timestamp"],
        unique=False,
    )

    op.create_index(
        "ix_gate_actions_gate_id",
        "gate_actions",
        ["gate_id"],
        unique=False,
    )

    op.create_index(
        "ix_gate_actions_staff_id",
        "gate_actions",
        ["staff_id"],
        unique=False,
    )

    op.create_index(
        "ix_gate_actions_access_event_id",
        "gate_actions",
        ["access_event_id"],
        unique=False,
    )


def downgrade() -> None:

    # ========================================================
    # GATE ACTIONS
    # ========================================================

    op.drop_index(
        "ix_gate_actions_access_event_id",
        table_name="gate_actions",
    )

    op.drop_index(
        "ix_gate_actions_staff_id",
        table_name="gate_actions",
    )

    op.drop_index(
        "ix_gate_actions_gate_id",
        table_name="gate_actions",
    )

    op.drop_index(
        "ix_gate_actions_timestamp",
        table_name="gate_actions",
    )

    op.drop_table(
        "gate_actions"
    )


    # ========================================================
    # STAFF ACCOUNTS
    # ========================================================

    op.drop_index(
        "ix_staff_accounts_role",
        table_name="staff_accounts",
    )

    op.drop_index(
        "ix_staff_accounts_username",
        table_name="staff_accounts",
    )

    op.drop_table(
        "staff_accounts"
    )