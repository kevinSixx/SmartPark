from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.access_event import AccessEvent
from backend.app.models.gate_action import GateAction
from backend.app.models.staff_account import StaffAccount
from backend.app.schemas.gate_action import (
    GateActionCreate,
)


def create_gate_action(
    db: Session,
    action_data: GateActionCreate,
) -> GateAction:

    # ========================================================
    # VALIDAR PERSONAL
    # ========================================================

    if action_data.staff_id is not None:

        staff = db.get(
            StaffAccount,
            action_data.staff_id,
        )

        if staff is None:
            raise HTTPException(
                status_code=404,
                detail="Staff account not found",
            )

        if not staff.active:
            raise HTTPException(
                status_code=400,
                detail="Staff account is inactive",
            )

    # ========================================================
    # VALIDAR EVENTO DE ACCESO
    # ========================================================

    if action_data.access_event_id is not None:

        access_event = db.get(
            AccessEvent,
            action_data.access_event_id,
        )

        if access_event is None:
            raise HTTPException(
                status_code=404,
                detail="Access event not found",
            )

    # ========================================================
    # REGLAS PARA ACCIONES MANUALES
    # ========================================================

    if action_data.source == "MANUAL":

        if action_data.staff_id is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Manual gate actions require "
                    "a staff account"
                ),
            )

        # Abrir manualmente SIEMPRE necesita motivo.
        if action_data.action == "OPEN":

            if (
                action_data.reason is None
                or not action_data.reason.strip()
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Manual OPEN requires "
                        "a reason"
                    ),
                )

    # ========================================================
    # CREAR REGISTRO
    # ========================================================

    gate_action = GateAction(
        **action_data.model_dump()
    )

    db.add(gate_action)
    db.commit()
    db.refresh(gate_action)

    return gate_action


def list_gate_actions(
    db: Session,
    gate_id: str | None = None,
    limit: int = 100,
) -> list[GateAction]:

    query = select(
        GateAction
    )

    if gate_id is not None:

        query = query.where(
            GateAction.gate_id
            == gate_id
        )

    query = (
        query
        .order_by(
            GateAction.timestamp.desc(),
            GateAction.id.desc(),
        )
        .limit(limit)
    )

    return list(
        db.scalars(query).all()
    )


def get_gate_action(
    db: Session,
    action_id: int,
) -> GateAction:

    gate_action = db.get(
        GateAction,
        action_id,
    )

    if gate_action is None:
        raise HTTPException(
            status_code=404,
            detail="Gate action not found",
        )

    return gate_action