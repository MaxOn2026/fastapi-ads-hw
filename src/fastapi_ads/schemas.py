from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

Role = Literal["user", "admin"]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    role: Role = "user"


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    role: Optional[Role] = None


class UserOut(BaseModel):
    id: int
    username: str
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True


class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, ge=0)


class AdvertisementOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author_id: Optional[int]
    author_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True