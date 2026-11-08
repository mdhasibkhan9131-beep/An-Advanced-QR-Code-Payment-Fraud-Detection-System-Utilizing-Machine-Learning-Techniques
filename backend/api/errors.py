"""
Centralized error handling conforming to RFC 7807 Problem Details.
"""

import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.config.logging_config import logger
from backend.api.schema import ProblemDetails, ErrorDetail


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles Pydantic input validation failures with field-level diagnostics."""
    details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Invalid value")
        details.append(ErrorDetail(field=field, issue=msg))

    logger.warning(f"Validation failure on {request.url.path}: {details}")

    problem = ProblemDetails(
        error_code="UNPROCESSABLE_ENTITY",
        message="Request payload failed structural schema or boundary validation.",
        status_code=422,
        timestamp=int(time.time() * 1000),
        details=details
    )
    return JSONResponse(
        status_code=422,
        content=problem.model_dump()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles standard HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    problem = ProblemDetails(
        error_code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        status_code=exc.status_code,
        timestamp=int(time.time() * 1000),
        details=[]
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Shields internal unhandled exceptions and prevents stack trace leakage."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    problem = ProblemDetails(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred while processing the transaction.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        timestamp=int(time.time() * 1000),
        details=[ErrorDetail(field=None, issue="Internal processing error. Diagnostic logged.")]
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem.model_dump()
    )
