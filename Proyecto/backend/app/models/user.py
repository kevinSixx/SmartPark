from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    institutional_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # ========================================================
    # RELACIONES EXISTENTES
    # ========================================================

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="user"
    )

    permissions: Mapped[list["Permission"]] = relationship(
        back_populates="user"
    )

    access_events: Mapped[list["AccessEvent"]] = relationship(
        back_populates="user"
    )

    # ========================================================
    # BIOMETRIA FACIAL
    # ========================================================

    # Un único perfil biométrico por usuario.
    face_profile: Mapped["FaceProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Varias fotografías de enrolamiento.
    face_samples: Mapped[list["FaceSample"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )