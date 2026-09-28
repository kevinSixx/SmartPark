from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class GateAction(Base):
    __tablename__ = "gate_actions"

    __table_args__ = (
        CheckConstraint(
            "action IN ('OPEN', 'CLOSE')",
            name="ck_gate_actions_action",
        ),
        CheckConstraint(
            "source IN ('AUTO', 'MANUAL')",
            name="ck_gate_actions_source",
        ),
        CheckConstraint(
            "status IN ('SUCCESS', 'ERROR')",
            name="ck_gate_actions_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    gate_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="gate-01",
        server_default="gate-01",
        index=True
    )

    action: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    staff_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "staff_accounts.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    access_event_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "access_events.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    observation: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SUCCESS",
        server_default="SUCCESS"
    )

    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )