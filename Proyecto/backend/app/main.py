import logging

from fastapi import (
    FastAPI,
    Request,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.responses import (
    JSONResponse,
)

from sqlalchemy import text

from backend.app.database import engine

from backend.app.routes.access_events import (
    router as access_router,
)

from backend.app.routes.auth import (
    router as auth_router,
)

from backend.app.routes.face_profiles import (
    router as face_profiles_router,
)

from backend.app.routes.gates import (
    router as gates_router,
)

from backend.app.routes.permissions import (
    router as permissions_router,
)

from backend.app.routes.staff import (
    router as staff_router,
)

from backend.app.routes.users import (
    router as users_router,
)

from backend.app.routes.vehicles import (
    router as vehicles_router,
)


logger = logging.getLogger(
    __name__
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="SmartPark UCE API",
    version="1.7.2"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://smartpark-uce-frontend-573672769830.s3-website-us-east-1.amazonaws.com",
        "https://production.d1kzks9pms1av2.amplifyapp.com",
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ============================================================
# ROUTERS EXISTENTES
# ============================================================

app.include_router(
    users_router,
    prefix="/api/v1"
)

app.include_router(
    vehicles_router,
    prefix="/api/v1"
)

app.include_router(
    permissions_router,
    prefix="/api/v1"
)

app.include_router(
    access_router,
    prefix="/api/v1"
)

app.include_router(
    face_profiles_router,
    prefix="/api/v1"
)


# ============================================================
# AUTENTICACION / PERSONAL / GARITAS
# ============================================================
#
# Estos routers ya contienen /api/v1
# dentro de sus propios archivos.
# ============================================================

app.include_router(
    auth_router
)

app.include_router(
    staff_router
)

app.include_router(
    gates_router
)


# ============================================================
# ERROR HANDLER
# ============================================================

@app.exception_handler(
    Exception
)
async def unexpected_error_handler(
    request: Request,
    exc: Exception
):

    logger.exception(
        "Unexpected error while processing %s",
        request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail":
                "Internal server error"
        },
    )


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health"
)
def health():

    return {
        "status":
            "ok",

        "service":
            "smartpark-api",

        "version":
            "1.7.2"
    }


# ============================================================
# DATABASE CHECK
# ============================================================

@app.get(
    "/db-check"
)
def db_check():

    with engine.connect() as connection:

        connection.execute(
            text(
                "SELECT 1"
            )
        )

    return {
        "status":
            "ok",

        "database":
            "connected"
    }