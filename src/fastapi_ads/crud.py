from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime

from . import models, schemas


def create_advertisement(db: Session, data: schemas.AdvertisementCreate) -> models.Advertisement:
    ad = models.Advertisement(**data.model_dump())
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


def get_advertisement(db: Session, ad_id: int) -> Optional[models.Advertisement]:
    return db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()


def update_advertisement(
    db: Session, ad_id: int, data: schemas.AdvertisementUpdate
) -> Optional[models.Advertisement]:
    ad = get_advertisement(db, ad_id)
    if not ad:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad


def delete_advertisement(db: Session, ad_id: int) -> bool:
    ad = get_advertisement(db, ad_id)
    if not ad:
        return False
    db.delete(ad)
    db.commit()
    return True


def search_advertisements(
    db: Session,
    title: Optional[str] = None,
    description: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    author: Optional[str] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
):
    query = db.query(models.Advertisement)

    filters = []
    if title:
        filters.append(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        filters.append(models.Advertisement.description.ilike(f"%{description}%"))
    if author:
        filters.append(models.Advertisement.author.ilike(f"%{author}%"))
    if price_min is not None:
        filters.append(models.Advertisement.price >= price_min)
    if price_max is not None:
        filters.append(models.Advertisement.price <= price_max)
    if created_from:
        filters.append(models.Advertisement.created_at >= created_from)
    if created_to:
        filters.append(models.Advertisement.created_at <= created_to)

    if filters:
        query = query.filter(and_(*filters))

    return query.order_by(models.Advertisement.created_at.desc()).offset(offset).limit(limit).all()