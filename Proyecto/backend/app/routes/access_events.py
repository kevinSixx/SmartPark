import os

import httpx

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
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
# CONFIGURACIÓN IA
#
# En AWS:
# AI_BASE_URL=http://172.31.33.54:8001
#
# En desarrollo local:
# http://localhost:8001
# ============================================================

AI_BASE_URL = (
    os.getenv(
        "AI_BASE_URL",
        "http://localhost:8001"
    )
    .strip()
    .rstrip("/")
)


AI_PROCESS_URL = (
    f"{AI_BASE_URL}/process"
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
# PROCESAR ACCESO DESDE FRONTEND
#
# Frontend
#   ↓
# Backend
#   ↓
# IA /process
#   ↓
# Face + OCR
#   ↓
# IA llama /access/authorize
#   ↓
# RDS + AWS IoT
# ============================================================

@router.post(
    "/access/process"
)
async def process_access(
    face_image: UploadFile = File(...),
    plate_image: UploadFile = File(...),
    event_type: str = Form("ENTRY")
):

    # --------------------------------------------------------
    # VALIDAR TIPO DE EVENTO
    # --------------------------------------------------------

    event_type = (
        event_type
        .strip()
        .upper()
    )


    if event_type not in (
        "ENTRY",
        "EXIT"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "event_type debe ser "
                "ENTRY o EXIT"
            )
        )


    # --------------------------------------------------------
    # LEER ARCHIVOS
    # --------------------------------------------------------

    face_contents = (
        await face_image.read()
    )

    plate_contents = (
        await plate_image.read()
    )


    if not face_contents:

        raise HTTPException(
            status_code=400,
            detail=(
                "La imagen del rostro "
                "está vacía."
            )
        )


    if not plate_contents:

        raise HTTPException(
            status_code=400,
            detail=(
                "La imagen de la placa "
                "está vacía."
            )
        )


    # --------------------------------------------------------
    # ENVIAR A SMARTPARK IA
    # --------------------------------------------------------

    try:

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                AI_PROCESS_URL,

                data={
                    "event_type":
                        event_type
                },

                files={
                    "face_image": (
                        face_image.filename
                        or
                        "face.jpg",

                        face_contents,

                        face_image.content_type
                        or
                        "image/jpeg"
                    ),

                    "plate_image": (
                        plate_image.filename
                        or
                        "plate.jpg",

                        plate_contents,

                        plate_image.content_type
                        or
                        "image/jpeg"
                    ),
                }
            )


            response.raise_for_status()


    except httpx.RequestError as error:

        raise HTTPException(
            status_code=503,
            detail=(
                "No se pudo conectar con "
                "SmartPark AI: "
                f"{error}"
            )
        ) from error


    except httpx.HTTPStatusError as error:

        detail = (
            error.response.text
        )


        try:

            body = (
                error.response.json()
            )

            detail = (
                body.get(
                    "detail"
                )
                or
                detail
            )

        except Exception:
            pass


        raise HTTPException(
            status_code=502,
            detail=(
                "SmartPark AI respondió "
                f"con error "
                f"{error.response.status_code}: "
                f"{detail}"
            )
        ) from error


    # --------------------------------------------------------
    # RESPUESTA IA
    # --------------------------------------------------------

    try:

        result = (
            response.json()
        )

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "SmartPark AI devolvió "
                "una respuesta inválida."
            )
        ) from error


    return result


# ============================================================
# AUTORIZAR ACCESO
#
# Este endpoint sigue siendo llamado por la IA después
# de reconocer rostro y placa.
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
    # EJECUTAR LÓGICA DE AUTORIZACIÓN
    # --------------------------------------------------------

    result = authorize_access(
        db,
        request
    )


    # --------------------------------------------------------
    # OBTENER DECISIÓN
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
    # AUTORIZADO
    #
    # Backend
    #   -> AWS IoT Core
    #   -> OPEN
    #   -> ESP32
    #   -> SG90
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
            "[ACCESS] Acceso no autorizado: "
            f"{decision}"
        )


    return result