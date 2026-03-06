from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

# Generic type for reusable pagination
T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    """
    Standard pagination response.

    This schema is used as a stable API contract
    for any list endpoint that supports pagination.
    """

    items: List[T] = Field(
        ..., description="Paginated list of items"
    )
    limit: int = Field(
        ..., ge=1, description="Number of items per page"
    )
    offset: int = Field(
        ..., ge=0, description="Pagination offset"
    )
    total: int = Field(
        ..., ge=0, description="Total number of items available"
    )