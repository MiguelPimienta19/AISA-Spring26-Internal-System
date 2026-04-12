from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import todos

app = FastAPI(
    title="AISA Internal System — Todo API",
    version="1.0.0",
    description="FastAPI Todo service for the AISA Spring 26 benchmark system.",
)


# --- Guardian / error handlers ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


# --- Routers ---

app.include_router(todos.router)


# --- Health check ---

@app.get("/", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "service": "Todo API"}
