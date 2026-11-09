from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, get_current_user_optional

router = APIRouter(prefix="/advertisement", tags=["advertisements"])


def _to_out(ad: models.Advertisement) -> schemas.AdvertisementOut:
    return schemas.AdvertisementOut(
        id=ad.id,
        title=ad.title,
        description=ad.description,
        price=ad.price,
        author_id=ad.author_id,
        author_username=ad.author.username if ad.author else None,
        created_at=ad.created_at,
    )


@router.get("", response_model=List[schemas.AdvertisementOut])
def search_advertisements(
    title: Optional[str] = None,
    description: Optional[str] = None,
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    author_id: Optional[int] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Advertisement)
    filters = []
    if title:
        filters.append(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        filters.append(models.Advertisement.description.ilike(f"%{description}%"))
    if price_min is not None:
        filters.append(models.Advertisement.price >= price_min)
    if price_max is not None:
        filters.append(models.Advertisement.price <= price_max)
    if author_id is not None:
        filters.append(models.Advertisement.author_id == author_id)
    if created_from:
        filters.append(models.Advertisement.created_at >= created_from)
    if created_to:
        filters.append(models.Advertisement.created_at <= created_to)
    if filters:
        query = query.filter(and_(*filters))

    rows = (
        query.order_by(models.Advertisement.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_to_out(r) for r in rows]


@router.get("/{advertisement_id}", response_model=schemas.AdvertisementOut)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ad = db.get(models.Advertisement, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return _to_out(ad)


@router.post(
    "",
    response_model=schemas.AdvertisementOut,
    status_code=status.HTTP_201_CREATED,
)
def create_advertisement(
    payload: schemas.AdvertisementCreate,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    ad = models.Advertisement(
        title=payload.title,
        description=payload.description,
        price=payload.price,
        author_id=current.id,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return _to_out(ad)


@router.patch("/{advertisement_id}", response_model=schemas.AdvertisementOut)
def update_advertisement(
    advertisement_id: int,
    payload: schemas.AdvertisementUpdate,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    ad = db.get(models.Advertisement, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    is_admin = current.role == "admin"
    is_owner = ad.author_id == current.id
    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return _to_out(ad)


@router.delete("/{advertisement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_advertisement(
    advertisement_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    ad = db.get(models.Advertisement, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    is_admin = current.role == "admin"
    is_owner = ad.author_id == current.id
    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db.delete(ad)
    db.commit()
    return None