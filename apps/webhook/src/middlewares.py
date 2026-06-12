from typing import Any, Callable
from uuid import uuid4

from fastapi import Request, Response


async def correlation_id_middleware(
    request: Request, call_next: Callable
) -> Any:
    """
    Middleware responsible for setting the correlation ID
    in the response headers.
    """
    correlation_id = request.headers.get("X-Correlation-ID")

    if not correlation_id:
        correlation_id = str(uuid4())

    request.state.correlation_id = correlation_id

    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
