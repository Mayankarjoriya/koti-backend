import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.project import Project
from models.user import User
from schemas.project import ProjectResponse
from services.cloudinary_service import upload_project_image, delete_project_image
from routers.auth import get_current_admin

router = APIRouter(tags=["Projects"])


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


# ─── Public endpoints ────────────────────────────────────────────────────────

@router.get("/api/projects", response_model=List[ProjectResponse])
async def list_projects(featured_only: bool = False, db: AsyncSession = Depends(get_db)):
    """List all projects. Optionally filter by is_featured."""
    query = select(Project)
    if featured_only:
        query = query.where(Project.is_featured == True)
    query = query.order_by(Project.order_index, Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    return [ProjectResponse.from_orm_custom(p) for p in projects]


@router.get("/api/projects/{slug}", response_model=ProjectResponse)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single project by its slug."""
    result = await db.execute(select(Project).where(Project.slug == slug))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return ProjectResponse.from_orm_custom(project)


# ─── Admin endpoints ──────────────────────────────────────────────────────────

@router.post("/api/admin/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),           # comma-separated: "React,FastAPI"
    link_url: Optional[str] = Form(None),
    is_featured: bool = Form(False),
    order_index: int = Form(0),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Create a new project. Optionally upload an image to Cloudinary."""
    slug = _slugify(title)

    # Ensure slug is unique
    result = await db.execute(select(Project).where(Project.slug == slug))
    if result.scalars().first():
        slug = f"{slug}-{str(uuid_short())}"

    image_url, cloudinary_id = None, None
    if image and image.filename:
        image_url, cloudinary_id = await upload_project_image(image)

    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    project = Project(
        title=title,
        slug=slug,
        description=description,
        image_url=image_url,
        cloudinary_id=cloudinary_id,
        tags=tag_list,
        link_url=link_url,
        is_featured=is_featured,
        order_index=str(order_index),
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.from_orm_custom(project)


@router.put("/api/admin/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    is_featured: Optional[bool] = Form(None),
    order_index: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Update a project. Uploading a new image replaces the old one in Cloudinary."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if title is not None:
        project.title = title
        project.slug = _slugify(title)
    if description is not None:
        project.description = description
    if tags is not None:
        project.tags = [t.strip() for t in tags.split(",")]
    if link_url is not None:
        project.link_url = link_url
    if is_featured is not None:
        project.is_featured = is_featured
    if order_index is not None:
        project.order_index = str(order_index)

    if image and image.filename:
        # Delete old image from Cloudinary
        if project.cloudinary_id:
            delete_project_image(project.cloudinary_id)
        project.image_url, project.cloudinary_id = await upload_project_image(image)

    await db.commit()
    await db.refresh(project)
    return ProjectResponse.from_orm_custom(project)


@router.delete("/api/admin/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Delete a project and its Cloudinary image."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if project.cloudinary_id:
        delete_project_image(project.cloudinary_id)

    await db.delete(project)
    await db.commit()


def uuid_short() -> str:
    import uuid
    return str(uuid.uuid4())[:8]
