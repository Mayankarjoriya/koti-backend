from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    link_url: Optional[str] = None
    is_featured: bool = False
    order_index: int = 0


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    link_url: Optional[str] = None
    is_featured: Optional[bool] = None
    order_index: Optional[int] = None


class ProjectResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    cloudinary_id: Optional[str]
    tags: Optional[List[str]]
    link_url: Optional[str]
    is_featured: bool
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj):
        return cls(
            id=obj.id,
            title=obj.title,
            slug=obj.slug,
            description=obj.description,
            image_url=obj.image_url,
            cloudinary_id=obj.cloudinary_id,
            tags=obj.tags or [],
            link_url=obj.link_url,
            is_featured=obj.is_featured,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
        )
