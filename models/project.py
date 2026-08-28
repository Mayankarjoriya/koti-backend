import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)       # Cloudinary secure URL
    cloudinary_id = Column(String(300), nullable=True)   # Cloudinary public_id for deletion
    tags = Column(JSON, default=list)                    # e.g. ["React", "FastAPI"]
    link_url = Column(String(500), nullable=True)        # Live demo or repo link
    is_featured = Column(Boolean, default=False)
    order_index = Column(String, default="0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
