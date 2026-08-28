from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.service_item import ServiceItem
from models.user import User
from schemas.service_item import ServiceCreate, ServiceUpdate, ServiceResponse
from routers.auth import get_current_admin

router = APIRouter(tags=["Services"])


# ─── Public endpoints ─────────────────────────────────────────────────────────

@router.get("/api/services", response_model=List[ServiceResponse])
async def list_services(db: AsyncSession = Depends(get_db)):
    """List all active services ordered by order_index."""
    result = await db.execute(
        select(ServiceItem)
        .where(ServiceItem.is_active == True)
        .order_by(ServiceItem.order_index)
    )
    return result.scalars().all()


@router.get("/api/services/all", response_model=List[ServiceResponse])
async def list_all_services(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """List ALL services including inactive ones (admin only)."""
    result = await db.execute(select(ServiceItem).order_by(ServiceItem.order_index))
    return result.scalars().all()


# ─── Admin endpoints ──────────────────────────────────────────────────────────

@router.post("/api/admin/services", response_model=ServiceResponse, status_code=201)
async def create_service(
    data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    service = ServiceItem(**data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.put("/api/admin/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    data: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(ServiceItem).where(ServiceItem.id == service_id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/api/admin/services/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(ServiceItem).where(ServiceItem.id == service_id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    await db.delete(service)
    await db.commit()
