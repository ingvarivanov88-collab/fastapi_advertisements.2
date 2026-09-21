from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# --- Пользователи ---
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserRead(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Авторизация ---
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Объявления ---
class AdvertisementBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class AdvertisementRead(AdvertisementBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True