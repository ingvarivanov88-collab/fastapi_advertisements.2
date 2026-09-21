from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from . import schemas, crud, auth
from .database import engine, Base, get_session

app = FastAPI(title="Advertisement API")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- ЛОГИН (JSON) ---
@app.post("/login", response_model=schemas.Token)
async def login(
    data: schemas.LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await crud.authenticate_user(session, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# --- ПОЛЬЗОВАТЕЛИ ---
@app.get("/user", response_model=List[schemas.UserRead])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(auth.require_user),
):
    return await crud.get_all_users(session)


@app.post("/user", response_model=schemas.UserRead, status_code=201)
async def create_user(data: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_user_by_username(session, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    return await crud.create_user(session, data)


@app.get("/user/{user_id}", response_model=schemas.UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/user/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: int,
    data: schemas.UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(auth.get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if data.role is not None and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can change role")
    user = await crud.update_user(session, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(auth.get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = await crud.delete_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}


# --- ОБЪЯВЛЕНИЯ ---
@app.post("/advertisement", response_model=schemas.AdvertisementRead, status_code=201)
async def create_advertisement(
    data: schemas.AdvertisementCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(auth.require_user),
):
    return await crud.create_advertisement(session, data, current_user.id)


@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementRead)
async def get_advertisement(advertisement_id: int, session: AsyncSession = Depends(get_session)):
    adv = await crud.get_advertisement(session, advertisement_id)
    if not adv:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return adv


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementRead)
async def update_advertisement(
    advertisement_id: int,
    data: schemas.AdvertisementUpdate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(auth.get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    adv = await crud.get_advertisement(session, advertisement_id)
    if not adv:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if current_user.role != "admin" and adv.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await crud.update_advertisement(session, advertisement_id, data)


@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(
    advertisement_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(auth.get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    adv = await crud.get_advertisement(session, advertisement_id)
    if not adv:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if current_user.role != "admin" and adv.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await crud.delete_advertisement(session, advertisement_id)
    return {"message": "Advertisement deleted"}


@app.get("/advertisement", response_model=List[schemas.AdvertisementRead])
async def search_advertisements(
    title: Optional[str] = None,
    description: Optional[str] = None,
    author_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
):
    return await crud.search_advertisements(
        session,
        title=title,
        description=description,
        author_id=author_id,
        min_price=min_price,
        max_price=max_price,
        created_from=created_from,
        created_to=created_to,
    )