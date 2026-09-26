import logging

from fastapi import (
    FastAPI,
    Request,
)

from fastapi.responses import (
    JSONResponse,
)

from sqlalchemy import text

from backend.app.database import engine

from backend.app.routes.access_events import (
    router as access_router,
)

from backend.app.routes.permissions import (
    router as permissions_router,
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
    version="1.1.0"
)


# ============================================================
# ROUTERS
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
        "status": "ok",
        "service": "smartpark-api"
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
        "status": "ok",
        "database": "connected"
    }