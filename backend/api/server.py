"""
FastAPI application entrypoint and middleware orchestration.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config.settings import settings
from backend.config.logging_config import logger
from backend.database.session import init_db
from backend.api.routes import router
from backend.api.errors import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks: startup and shutdown."""
    logger.info("Initializing system foundation...")
    try:
        init_db()
        logger.info("Database schemas and SQLite WAL engine initialized.")
        from backend.api.routes import get_model_container
        get_model_container()
        logger.info("Production ML models pre-warmed for immediate sub-100ms inference.")
    except Exception as e:
        logger.error(f"Critical error during database startup: {e}")

    yield

    logger.info("System shutting down cleanly.")


def create_app() -> FastAPI:
    """Application factory for FastAPI microservice."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="High-Throughput, Low-Latency QR Payment Fraud Detection Engine",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Timing Middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Response-Time-Ms"] = f"{process_time_ms:.2f}"
        return response

    # Exception Handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Mount Route Handlers
    app.include_router(router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.server:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )

