from typing import Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from secret_manager.db.models import Token
from .decorators import commit
from sqlalchemy import select, update, delete


#token
#user_id
#key_id
#permissions
#sec_level


#создает новый токен
@commit
async def create_token(session: AsyncSession, token: str, user_id: int, key_id: int, permissions: List[str] | Tuple[str, ...], sec_level: int) -> Token:
    token = Token(
        token=token,
        user_id=user_id,
        key_id=key_id,
        permissions=permissions,
        sec_level=sec_level
    )
    session.add(token)
    return token


#получить токен
async def get_token(session: AsyncSession, token: str) -> None | Token:
    stmt = select(Token).where(Token.token == token)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


#обновить шифрующий ключ токена
@commit
async def update_key(session: AsyncSession, token: str, new_key_id: int) -> bool:
    stmt = update(Token).where(Token.token == token).values(key_id = new_key_id)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True


@commit
async def del_token(session: AsyncSession, token: str) -> bool:
    stmt = delete(Token).where(Token.token == token)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True
