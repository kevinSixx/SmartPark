from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class FaceProfile(Base):
    __tablename__ = "face_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False,
        index=True
    )

    # Vector ArcFace de 512 dimensiones.
    # Ejemplo:
    # [
    #     0.0123,
    #     -0.0541,
    #     ...
    # ]
    embedding: Mapped[list] = mapped_column(
        JSONB,
        nullable=False
    )

    embedding_dimension: Mapped[int] = mapped_column(
        Integer,
        default=512,
        server_default="512",
        nullable=False
    )

    model_name: Mapped[str] = mapped_column(
        String(50),
        default="ArcFace",
        server_default="ArcFace",
        nullable=False
    )

    detector_backend: Mapped[str] = mapped_column(
        String(50),
        default="retinaface",
        server_default="retinaface",
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="face_profile"
    )