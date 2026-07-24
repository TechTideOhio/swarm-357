"""Structured JSON request logging with correlation IDs for the HTTP API."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

logger = logging.getLogger("techtide_swarm.http")


class CorrelationIdASGIMiddleware:
    """Pure ASGI: injects X-Correlation-ID on the response and logs one JSON line per request."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw_headers = scope.get("headers") or []
        cid: str | None = None
        for key, value in raw_headers:
            if key == b"x-correlation-id":
                cid = value.decode("latin-1")
                break
        if cid is None:
            cid = str(uuid.uuid4())

        started = time.perf_counter()
        status_code: dict[str, int] = {"v": 0}

        async def send_wrapper(message: Any) -> None:
            if message["type"] == "http.response.start":
                status_code["v"] = int(message.get("status", 0))
                hdrs = list(message.get("headers", []))
                hdrs.append((b"x-correlation-id", cid.encode("latin-1")))
                message = {**message, "headers": hdrs}
            elif message["type"] == "http.response.body" and not message.get("more_body", False):
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                entry = {
                    "msg": "http_request",
                    "correlation_id": cid,
                    "method": scope.get("method", ""),
                    "path": scope.get("path", ""),
                    "status_code": status_code["v"],
                    "elapsed_ms": elapsed_ms,
                }
                logger.info(json.dumps(entry))
            await send(message)

        await self.app(scope, receive, send_wrapper)
