import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.config import settings
from backend.core.errors import (
    HealthcareAPIException,
    healthcare_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from backend.core.rate_limiter import RateLimitMiddleware
from backend.api.v1.api import api_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces OWASP-recommended HTTP security headers across all API responses (NFR-02)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
        )
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler managing application startup and shutdown lifecycle."""
    # Startup: Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    # Shutdown: Perform any cleanup operations


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "MediCare AI - Production-grade asynchronous REST API backend "
        "powering RAG-based health education, medical report analysis, "
        "medication tracking, appointment scheduling, and clinical governance."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# 1. Register Security Headers Middleware (OWASP Hardening - NFR-02)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Register Rate Limiting Middleware (NFR-02 & FR-08.2)
app.add_middleware(RateLimitMiddleware)

# 3. Register Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register Global Standardized Exception Handlers (NFR-03.2)
app.add_exception_handler(HealthcareAPIException, healthcare_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 3. Mount API v1 Master Router
app.include_router(api_router, prefix=settings.API_V1_STR)


# 4. Top-level Root & Diagnostic Endpoints
@app.get("/", status_code=status.HTTP_200_OK, tags=["Root"])
async def root():
    """Top-level welcome endpoint with API documentation links."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1_base": settings.API_V1_STR,
        "health_check": f"{settings.API_V1_STR}/health",
    }


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Root"])
async def root_health():
    """Top-level health check endpoint for reverse-proxies and container probes."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
