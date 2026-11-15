from fastapi import APIRouter, status
from typing import Dict, Any
from backend.core.config import settings

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Returns platform operational health status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "api_server": "online",
            "cors_configured": True,
            "emergency_guardrails": "active"
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    """Root platform welcome endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API v1",
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_STR}/health"
    }
