from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from . import crud, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service", version="1.0.0")


@app.post(
    "/advertisement",
    response_model=schemas.AdvertisementOut,
    status_code=status.HTTP_201_CREATED,
)
def create_advertisement(
    ad: schemas.AdvertisementCreate, db: Session = Depends(get_db)
):
    return crud.create_advertisement(db, ad)


@app.get("/advertisement", response_model=List[schemas.AdvertisementOut])
def search_advertisements(
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    author: Optional[str] = Query(None),
    created_from: Optional[datetime] = Query(None),
    created_to: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.search_advertisements(
        db,
        title=title,
        description=description,
        price_min=price_min,
        price_max=price_max,
        author=author,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )


@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementOut)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ad = crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementOut)
def update_advertisement(
    advertisement_id: int,
    payload: schemas.AdvertisementUpdate,
    db: Session = Depends(get_db),
):
    ad = crud.update_advertisement(db, advertisement_id, payload)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.delete(
    "/advertisement/{advertisement_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_advertisement(db, advertisement_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return None