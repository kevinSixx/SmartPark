from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
)

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.mqtt.client import (
    open_and_close_barrier,
)

from backend.app.schemas.access_event import (
    AccessEventCreate,
    AccessEventResponse,
    AuthorizationRequest,
    AuthorizationResponse,
)

from backend.app.services.access_events import (
    create_access_event,
    get_access_event,
    list_access_events,
)

from backend.app.services.authorization import (
    authorize_access,
)


router = APIRouter(
    tags=["Access"]
)


# ============================================================
# REGISTRAR EVENTO
# ============================================================

@router.post(
    "/access-events",
    response_model=AccessEventResponse,
    status_code=201
)
def register_access_event(
    event_data: AccessEventCreate,
    db: Session = Depends(get_db)
):

    return create_access_event(
        db,
        event_data
    )


# ============================================================
# LISTAR EVENTOS
# ============================================================

@router.get(
    "/access-events",
    response_model=list[AccessEventResponse]
)
def read_access_events(
    db: Session = Depends(get_db)
):

    return list_access_events(
        db
    )


# ============================================================
# OBTENER EVENTO
# ============================================================

@router.get(
    "/access-events/{event_id}",
    response_model=AccessEventResponse
)
def read_access_event(
    event_id: int,
    db: Session = Depends(get_db)
):

    return get_access_event(
        db,
        event_id
    )


# ============================================================
# AUTORIZAR ACCESO
# ============================================================

@router.post(
    "/access/authorize",
    response_model=AuthorizationResponse
)
def authorize(
    request: AuthorizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Ejecutar la misma logica que ya teniamos
    # --------------------------------------------------------

    result = authorize_access(
        db,
        request
    )


    # --------------------------------------------------------
    # Obtener decision
    #
    # Compatible tanto si authorize_access devuelve
    # un modelo Pydantic como si devuelve un dict.
    # --------------------------------------------------------

    if isinstance(
        result,
        dict
    ):

        decision = result.get(
            "decision"
        )

    else:

        decision = getattr(
            result,
            "decision",
            None
        )


    # --------------------------------------------------------
    # SI ESTA AUTORIZADO:
    #
    # FastAPI
    #   -> AWS IoT Core
    #   -> OPEN
    #   -> ESP32
    #   -> SG90
    #
    # Y después de unos segundos:
    #
    #   -> CLOSE
    # --------------------------------------------------------

    if decision == "AUTHORIZED":

        print(
            "[ACCESS] AUTHORIZED. "
            "Programando apertura de barrera."
        )


        background_tasks.add_task(
            open_and_close_barrier
        )

    else:

        print(
            f"[ACCESS] Acceso no autorizado: "
            f"{decision}"
        )


    return result