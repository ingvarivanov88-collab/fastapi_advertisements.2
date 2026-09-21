from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from . import models, schemas
from .auth import hash_password, verify_password


# --- Пользователи ---
async def create_user(session: AsyncSession, data: schemas.UserCreate):
    user = models.User(
        username=data.username,
        password_hash=hash_password(data.password),
        role="user"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int):
    return await session.get(models.User, user_id)


async def get_all_users(session: AsyncSession):
    result = await session.execute(select(models.User))
    return result.scalars().all()


async def get_user_by_username(session: AsyncSession, username: str):
    result = await session.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()


async def update_user(session: AsyncSession, user_id: int, data: schemas.UserUpdate):
    user = await session.get(models.User, user_id)
    if not user:
        return None
    if data.username is not None:
        user.username = data.username
    if data.password is not None:
        user.password_hash = hash_password(data.password)
    if data.role is not None:
        user.role = data.role
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user_id: int):
    user = await session.get(models.User, user_id)
    if not user:
        return None
    await session.delete(user)
    await session.commit()
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await get_user_by_username(session, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


# --- Объявления ---
async def create_advertisement(session: AsyncSession, data: schemas.AdvertisementCreate, author_id: int):
    adv = models.Advertisement(**data.dict(), author_id=author_id)
    session.add(adv)
    await session.commit()
    await session.refresh(adv)
    return adv


async def get_advertisement(session: AsyncSession, adv_id: int):
    return await session.get(models.Advertisement, adv_id)


async def update_advertisement(session: AsyncSession, adv_id: int, data: schemas.AdvertisementUpdate):
    adv = await session.get(models.Advertisement, adv_id)
    if not adv:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(adv, field, value)
    await session.commit()
    await session.refresh(adv)
    return adv


async def delete_advertisement(session: AsyncSession, adv_id: int):
    adv = await session.get(models.Advertisement, adv_id)
    if not adv:
        return None
    await session.delete(adv)
    await session.commit()
    return adv


async def search_advertisements(
    session: AsyncSession,
    title: str = None,
    description: str = None,
    author_id: int = None,
    min_price: float = None,
    max_price: float = None,
    created_from: datetime = None,
    created_to: datetime = None,
):
    query = select(models.Advertisement)
    if title:
        query = query.where(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        query = query.where(models.Advertisement.description.ilike(f"%{description}%"))
    if author_id:
        query = query.where(models.Advertisement.author_id == author_id)
    if min_price is not None:
        query = query.where(models.Advertisement.price >= min_price)
    if max_price is not None:
        query = query.where(models.Advertisement.price <= max_price)
    if created_from:
        query = query.where(models.Advertisement.created_at >= created_from)
    if created_to:
        query = query.where(models.Advertisement.created_at <= created_to)
    result = await session.execute(query)
    return result.scalars().all()