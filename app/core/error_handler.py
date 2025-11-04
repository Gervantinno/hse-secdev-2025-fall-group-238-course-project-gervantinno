import json
import logging
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def problem(
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    extras: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Create an RFC 7807-compatible JSON response.

    This helper generates a correlation_id, logs a masked summary and returns
    a Starlette/ FastAPI JSONResponse with media type application/problem+json.
    """
    cid = str(uuid4())
    payload: Dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": cid,
    }
    if extras:
        payload.update(extras)

    log_payload = {
        "type": type_,
        "title": title,
        "status": status,
        "correlation_id": cid,
    }
    logger.error("problem response: %s", json.dumps(log_payload))

    return JSONResponse(
        content=payload, status_code=status, media_type="application/problem+json"
    )


async def rfc7807_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """A minimal exception handler that masks internals for unexpected errors.

    Integration: in FastAPI app use
        app.add_exception_handler(Exception, rfc7807_exception_handler)
    """
    detail = str(exc) if isinstance(exc, ValueError) else "internal server error"
    return problem(500, "Internal Server Error", detail)
