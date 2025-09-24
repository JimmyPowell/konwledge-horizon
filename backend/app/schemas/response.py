from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class UnifiedResponse(BaseModel, Generic[T]):
    code: int = Field(200, description="Status code")
    message: str = Field("Success", description="Response message")
    data: Optional[T] = None
