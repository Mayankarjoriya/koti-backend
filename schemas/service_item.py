from typing import Optional
from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    icon_name: Optional[str] = None
    is_active: bool = True
    order_index: int = 0


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    icon_name: Optional[str] = None
    is_active: Optional[bool] = None
    order_index: Optional[int] = None


class ServiceResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    icon_name: Optional[str]
    is_active: bool
    order_index: int

    class Config:
        from_attributes = True
