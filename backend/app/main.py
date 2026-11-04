import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

from .auth.router import router as auth_router
from .config import settings
from .measurements.router import router as measurements_router
from .sensors.router import router as sensors_router
from .series.router import router as series_router
from .users.router import router as users_router


def _operation_id(route: APIRoute) -> str:
    # Plain function names as OpenAPI operation ids -> short generated client names.
    return route.name


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    generate_unique_id_function=_operation_id,
)

app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(
    auth_router, prefix=settings.AUTH_STR, tags=["Authorization & Profile"]
)
app.include_router(
    sensors_router, prefix=f"{settings.API_V1_STR}/sensors", tags=["Sensors"]
)
app.include_router(
    measurements_router, prefix="/api/measurements", tags=["Measurements"]
)
app.include_router(series_router, prefix="/api/series", tags=["Series"])


@app.get("/health", tags=["Health Check"])
async def get_health() -> dict[str, str]:
    return {"status": "OK", "version": app.version}


if __name__ == "__main__":
    log_level = "debug" if settings.ENVIRONMENT == "dev" else "info"
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level=log_level)
