from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Optional


class HealthcareAPIException(Exception):
    """Base exception for all domain-specific API errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(message)


class ResourceNotFoundException(HealthcareAPIException):
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with identifier '{resource_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class UnauthorizedException(HealthcareAPIException):
    def __init__(self, detail: str = "Invalid or expired authentication credentials."):
        super().__init__(
            message="Unauthorized access.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenException(HealthcareAPIException):
    def __init__(self, detail: str = "Operation not permitted for your user role."):
        super().__init__(
            message="Forbidden action.",
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class EmergencySafetyTriggered(HealthcareAPIException):
    """Triggered when an emergency clinical keyword is detected in a query."""
    def __init__(self, keywords_detected: list):
        super().__init__(
            message="Emergency safety guardrail triggered.",
            status_code=status.HTTP_200_OK,  # 200 OK because it returns triage directive to client
            detail={
                "emergency": True,
                "keywords": keywords_detected,
                "warning": "Critical symptom detected. Please call emergency services (112 / 911) or proceed to the nearest emergency room immediately.",
                "action": "HALT_LLM_GENERATION"
            }
        )


# Global Exception Handlers conforming strictly to NFR-03.2
async def healthcare_exception_handler(request: Request, exc: HealthcareAPIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "detail": exc.detail
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    # Format readable error messages
    error_messages = [f"{err.get('loc', ['field'])[-1]}: {err.get('msg', 'invalid')}" for err in errors]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Input validation failed. Please check submitted fields.",
            "detail": error_messages
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail if isinstance(exc.detail, str) else "HTTP error encountered.",
            "detail": exc.detail
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "detail": str(exc) if request.app.debug else "Please contact platform support."
        }
    )
