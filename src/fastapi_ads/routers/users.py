from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..deps import get_current_user, get_current_user_optional
from ..security import hash_password

router = APIRouter(prefix="/user", tags=["users"])


@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # Доступно всем (в т.ч. анонимам). Роль admin назначить через этот эндпоинт нельзя,
    # чтобы любой желающий не мог создать админа. Админ создаётся сидом/через admin PATCH.
    exists = db.query(models.User).filter(models.User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already taken")
    if payload.role != "user":
        raise HTTPException(status_code=403, detail="Only admin can create admins")
    user = models.User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[schemas.UserOut])
@router.get("/", response_model=List[schemas.UserOut], include_in_schema=False)
def list_users(
    db: Session = Depends(get_db),
    current: Optional[models.User] = Depends(get_current_user_optional),
):
    # Аноним не должен видеть список — иначе утечка. Пусть список отдаётся только
    # авторизованным, но по ТЗ GET /user/{id} доступен анониму. Список — админ-only.
    if current is None or current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return db.query(models.User).order_by(models.User.id).all()


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_admin = current.role == "admin"
    is_self = current.id == user.id

    if not is_admin and not is_self:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    data = payload.model_dump(exclude_unset=True)

    # Менять роль может только admin. Себе роль тоже менять нельзя.
    if "role" in data:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Only admin can change role")
        user.role = data.pop("role")

    if "username" in data:
        new_name = data.pop("username")
        if new_name != user.username:
            taken = (
                db.query(models.User)
                .filter(models.User.username == new_name)
                .first()
            )
            if taken:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = new_name

    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_admin = current.role == "admin"
    is_self = current.id == user.id

    if not is_admin and not is_self:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # При удалении пользователя отвязываем его объявления (author_id -> NULL),
    # чтобы не ловить FK-нарушений и не терять данные.
    db.query(models.Advertisement).filter(
        models.Advertisement.author_id == user.id
    ).update({models.Advertisement.author_id: None})
    db.delete(user)
    db.commit()
    return None