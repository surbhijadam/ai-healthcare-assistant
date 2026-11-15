from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard success API response wrapper."""
    status: str = "success"
    message: str
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper conforming to NFR-03.2."""
    status: str = "error"
    message: str
    detail: Optional[Any] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
