from typing import Sequence, List

from sqlalchemy.ext.asyncio import AsyncSession
from secret_manager.db.models import Secret
from .decorators import commit
from sqlalchemy import select, update, delete



#создает секрет
@commit
async def create_secret(session: AsyncSession, name: str, user_id: int, key_id: int, sec_level: int,
                        secret: bytes, tag: bytes, nonce: bytes, datatype: str) -> Secret:
    secret = Secret(
        name=name,
        user_id=user_id,
        key_id=key_id,
        sec_level=sec_level,
        secret=secret,
        tag=tag,
        nonce=nonce,
        datatype=datatype
    )
    session.add(secret)
    return secret


#возвращает секрет по id
async def get_secret(session: AsyncSession, secret_id: int) -> Secret | None:
    stmt = select(Secret).where(Secret.id == secret_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


#возвращает id секретов по имени
async def get_ids_by_name(session: AsyncSession, user_id: int, name: str) -> Sequence:
    stmt = select(Secret.id).where((Secret.user_id == user_id) & (Secret.name == name))
    result = await session.execute(stmt)
    return result.scalars().all()


#обновляет уровень безопасности(sec_level) секрета
@commit
async def update_sec_level(session: AsyncSession, secret_id: int, new_sec_level: int) -> bool:
    stmt = update(Secret).where(Secret.id == secret_id).values(sec_level = new_sec_level)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True


#возвращает id секретов пользователя по страницам
async def get_user_secrets(session: AsyncSession, user_id: int, offset: int, limit: int) -> Sequence[Secret]:
    stmt = select(Secret).where(Secret.user_id == user_id).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
