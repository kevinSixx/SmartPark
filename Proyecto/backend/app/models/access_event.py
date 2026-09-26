from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class AccessEvent(Base):
    __tablename__ = "access_events"
    __table_args__ = (
        CheckConstraint("event_type IN ('ENTRY', 'EXIT')", name="ck_access_events_type"),
        CheckConstraint(
            "decision IN ('AUTHORIZED', 'REJECTED', 'REVIEW')",
            name="ck_access_events_decision",
        ),
        CheckConstraint(
            "face_score IS NULL OR (face_score >= 0 AND face_score <= 1)",
            name="ck_access_events_face_score",
        ),
        CheckConstraint(
            "plate_score IS NULL OR (plate_score >= 0 AND plate_score <= 1)",
            name="ck_access_events_plate_score",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(10), nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True
    )
    detected_plate: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    face_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    plate_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="access_events")
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="access_events")
