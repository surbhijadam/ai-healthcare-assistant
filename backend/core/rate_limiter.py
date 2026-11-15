import time
from typing import Dict, List, Tuple, Optional
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimiter:
    """
    In-memory sliding-window rate limiter for brute-force mitigation
    and endpoint abuse prevention (NFR-02 & FR-08.2).
    """

    def __init__(self, requests_per_minute: int = 300, login_attempts_per_minute: int = 15):
        self.requests_per_minute = requests_per_minute
        self.login_attempts_per_minute = login_attempts_per_minute
        self._clients: Dict[str, List[float]] = {}
        self._login_attempts: Dict[str, List[float]] = {}

    def _cleanup_window(self, timestamps: List[float], window_seconds: float = 60.0) -> List[float]:
        now = time.time()
        threshold = now - window_seconds
        return [t for t in timestamps if t > threshold]

    def check_rate_limit(self, client_ip: str, endpoint: str = "") -> Tuple[bool, int]:
        """
        Checks if client IP has exceeded the allowed rate limit.
        Returns: (is_limited: bool, retry_after_seconds: int)
        """
        now = time.time()
        is_login = "/auth/login" in endpoint.lower()
        limit = self.login_attempts_per_minute if is_login else self.requests_per_minute
        store = self._login_attempts if is_login else self._clients

        current_timestamps = store.get(client_ip, [])
        active_timestamps = self._cleanup_window(current_timestamps, 60.0)

        if len(active_timestamps) >= limit:
            retry_after = int(active_timestamps[0] + 60.0 - now) + 1
            store[client_ip] = active_timestamps
            return True, max(1, retry_after)

        active_timestamps.append(now)
        store[client_ip] = active_timestamps
        return False, 0

    def reset(self):
        """Clears all tracked client rates (useful for test resets)."""
        self._clients.clear()
        self._login_attempts.clear()


rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware applying rate limits per client IP.
    Whitelists local health checks and allows high-throughput testing.
    """

    async def dispatch(self, request: Request, call_next):
        # Exclude internal health checks and docs from rate limiting
        path = request.url.path
        if path in ("/health", "/api/v1/health", "/", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"

        is_limited, retry_after = rate_limiter.check_rate_limit(client_ip, endpoint=path)
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "message": "Too many requests. Please slow down.",
                    "detail": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
