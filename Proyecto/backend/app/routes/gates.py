from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.models.staff_account import (
    StaffAccount,
)

from backend.app.mqtt.client import (
    publish_command,
)

from backend.app.schemas.gate_action import (
    GateActionCreate,
    GateActionResponse,
    ManualGateActionRequest,
)

from backend.app.services.auth import (
    get_current_staff,
)

from backend.app.services.gate_actions import (
    create_gate_action,
    list_gate_actions,
)


router = APIRouter(
    prefix="/api/v1/gates",
    tags=["Gates"],
)


# ============================================================
# ABRIR BARRERA MANUALMENTE
# ADMIN / GUARD
# ============================================================

@router.post(
    "/{gate_id}/open",
    response_model=GateActionResponse,
)
def open_gate(
    gate_id: str,

    request: ManualGateActionRequest,

    db: Session = Depends(get_db),

    current_staff: StaffAccount
        = Depends(get_current_staff),
):

    # ========================================================
    # OPEN MANUAL REQUIERE MOTIVO
    # ========================================================

    if (
        request.reason is None
        or not request.reason.strip()
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Debe indicar un motivo "
                "para abrir la barrera manualmente"
            ),
        )

    # ========================================================
    # AWS IOT
    # ========================================================

    try:

        published = publish_command(
            "OPEN"
        )

        if not published:

            return create_gate_action(
                db,
                GateActionCreate(
                    gate_id=gate_id,

                    action="OPEN",

                    source="MANUAL",

                    staff_id=current_staff.id,

                    access_event_id=(
                        request.access_event_id
                    ),

                    reason=(
                        request.reason
                    ),

                    observation=(
                        request.observation
                    ),

                    status="ERROR",

                    error_message=(
                        "AWS IoT está deshabilitado"
                    ),
                ),
            )

        return create_gate_action(
            db,
            GateActionCreate(
                gate_id=gate_id,

                action="OPEN",

                source="MANUAL",

                staff_id=current_staff.id,

                access_event_id=(
                    request.access_event_id
                ),

                reason=(
                    request.reason
                ),

                observation=(
                    request.observation
                ),

                status="SUCCESS",
            ),
        )

    except HTTPException:

        raise

    except Exception as error:

        gate_action = create_gate_action(
            db,
            GateActionCreate(
                gate_id=gate_id,

                action="OPEN",

                source="MANUAL",

                staff_id=current_staff.id,

                access_event_id=(
                    request.access_event_id
                ),

                reason=(
                    request.reason
                ),

                observation=(
                    request.observation
                ),

                status="ERROR",

                error_message=(
                    str(error)[:500]
                ),
            ),
        )

        raise HTTPException(
            status_code=503,
            detail={
                "message":
                    "No se pudo abrir la barrera",

                "gate_action_id":
                    gate_action.id,

                "error":
                    str(error),
            },
        )


# ============================================================
# CERRAR BARRERA MANUALMENTE
# ADMIN / GUARD
# ============================================================

@router.post(
    "/{gate_id}/close",
    response_model=GateActionResponse,
)
def close_gate(
    gate_id: str,

    request: ManualGateActionRequest,

    db: Session = Depends(get_db),

    current_staff: StaffAccount
        = Depends(get_current_staff),
):

    try:

        published = publish_command(
            "CLOSE"
        )

        if not published:

            return create_gate_action(
                db,
                GateActionCreate(
                    gate_id=gate_id,

                    action="CLOSE",

                    source="MANUAL",

                    staff_id=current_staff.id,

                    access_event_id=(
                        request.access_event_id
                    ),

                    reason=(
                        request.reason
                        or "Cierre manual"
                    ),

                    observation=(
                        request.observation
                    ),

                    status="ERROR",

                    error_message=(
                        "AWS IoT está deshabilitado"
                    ),
                ),
            )

        return create_gate_action(
            db,
            GateActionCreate(
                gate_id=gate_id,

                action="CLOSE",

                source="MANUAL",

                staff_id=current_staff.id,

                access_event_id=(
                    request.access_event_id
                ),

                reason=(
                    request.reason
                    or "Cierre manual"
                ),

                observation=(
                    request.observation
                ),

                status="SUCCESS",
            ),
        )

    except HTTPException:

        raise

    except Exception as error:

        gate_action = create_gate_action(
            db,
            GateActionCreate(
                gate_id=gate_id,

                action="CLOSE",

                source="MANUAL",

                staff_id=current_staff.id,

                access_event_id=(
                    request.access_event_id
                ),

                reason=(
                    request.reason
                    or "Cierre manual"
                ),

                observation=(
                    request.observation
                ),

                status="ERROR",

                error_message=(
                    str(error)[:500]
                ),
            ),
        )

        raise HTTPException(
            status_code=503,
            detail={
                "message":
                    "No se pudo cerrar la barrera",

                "gate_action_id":
                    gate_action.id,

                "error":
                    str(error),
            },
        )


# ============================================================
# HISTORIAL DE ACCIONES
# ADMIN / GUARD
# ============================================================

@router.get(
    "/{gate_id}/actions",
    response_model=list[GateActionResponse],
)
def get_gate_actions(
    gate_id: str,

    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),

    db: Session = Depends(get_db),

    current_staff: StaffAccount
        = Depends(get_current_staff),
):

    return list_gate_actions(
        db,
        gate_id=gate_id,
        limit=limit,
    )