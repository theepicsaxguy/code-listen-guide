"""Middleware helpers for security headers and request throttling."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Deque, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach opinionated security headers to every response."""

    def __init__(
        self,
        app,
        *,
        content_security_policy: str,
        referrer_policy: str,
        enable_hsts: bool = False,
    ) -> None:
        super().__init__(app)
        self._csp = content_security_policy
        self._referrer_policy = referrer_policy
        self._enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("Content-Security-Policy", self._csp)
        response.headers.setdefault("Referrer-Policy", self._referrer_policy)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Permissions-Policy", "microphone=()")
        if self._enable_hsts and request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Throttle requests per client over a fixed window."""

    def __init__(
        self,
        app,
        *,
        max_requests: int,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self._default_max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: Dict[str, Deque[float]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next) -> Response:
        identifier = self._identify(request)
        max_requests = getattr(request.app.state, "rate_limit_per_minute", self._default_max_requests)
        async with self._lock:
            now = time.monotonic()
            window_start = now - self._window_seconds
            bucket = self._requests.setdefault(identifier, deque())
            while bucket and bucket[0] < window_start:
                bucket.popleft()
            if len(bucket) >= max_requests:
                return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
            bucket.append(now)
        return await call_next(request)

    def _identify(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = request.client
        if client:
            return f"ip:{client.host}"
        return "ip:unknown"
