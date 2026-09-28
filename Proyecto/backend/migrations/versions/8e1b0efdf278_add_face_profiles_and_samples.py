"""add face profiles and samples

Revision ID: 8e1b0efdf278
Revises: 0945aa4d18a8
Create Date: 2026-09-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# ============================================================
# ALEMBIC
# ============================================================

revision: str = "8e1b0efdf278"

down_revision: Union[str, None] = "0945aa4d18a8"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:

    # ========================================================
    # FACE PROFILES
    #
    # Un perfil biométrico por usuario.
    #
    # embedding:
    # Vector ArcFace de 512 dimensiones.
    #
    # Para este prototipo se almacena como JSONB.
    # ========================================================

    op.create_table(

        "face_profiles",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "embedding",
            postgresql.JSONB(),
            nullable=False
        ),

        sa.Column(
            "embedding_dimension",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("512")
        ),

        sa.Column(
            "model_name",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'ArcFace'")
        ),

        sa.Column(
            "detector_backend",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'retinaface'")
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_face_profiles_user_id_users",
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint(
            "id",
            name="pk_face_profiles"
        ),

        sa.UniqueConstraint(
            "user_id",
            name="uq_face_profiles_user_id"
        )
    )


    op.create_index(
        "ix_face_profiles_user_id",
        "face_profiles",
        ["user_id"],
        unique=False
    )


    op.create_index(
        "ix_face_profiles_is_active",
        "face_profiles",
        ["is_active"],
        unique=False
    )


    # ========================================================
    # FACE SAMPLES
    #
    # Aquí NO guardamos las imágenes.
    #
    # Las imágenes estarán en Amazon S3.
    # RDS solamente guarda la referencia s3_key.
    # ========================================================

    op.create_table(

        "face_samples",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "s3_key",
            sa.String(length=512),
            nullable=False
        ),

        sa.Column(
            "original_filename",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "content_type",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "quality_score",
            sa.Float(),
            nullable=True
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_face_samples_user_id_users",
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint(
            "id",
            name="pk_face_samples"
        ),

        sa.UniqueConstraint(
            "s3_key",
            name="uq_face_samples_s3_key"
        )
    )


    op.create_index(
        "ix_face_samples_user_id",
        "face_samples",
        ["user_id"],
        unique=False
    )


    op.create_index(
        "ix_face_samples_is_active",
        "face_samples",
        ["is_active"],
        unique=False
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:

    # ========================================================
    # FACE SAMPLES
    # ========================================================

    op.drop_index(
        "ix_face_samples_is_active",
        table_name="face_samples"
    )

    op.drop_index(
        "ix_face_samples_user_id",
        table_name="face_samples"
    )

    op.drop_table(
        "face_samples"
    )


    # ========================================================
    # FACE PROFILES
    # ========================================================

    op.drop_index(
        "ix_face_profiles_is_active",
        table_name="face_profiles"
    )

    op.drop_index(
        "ix_face_profiles_user_id",
        table_name="face_profiles"
    )

    op.drop_table(
        "face_profiles"
    )