from sqlalchemy.ext.asyncio import AsyncSession
from secret_manager.db.models import User
from .decorators import commit
from sqlalchemy import select, update, delete

#id
#name
#pass_hash
#create_date


#создание пользователя
@commit
async def create_user(session: AsyncSession, name: str, pass_hash: str, pass_sault: str) -> User:
    user = User(
        name=name,
        pass_hash=pass_hash,
        pass_sault=pass_sault
    )
    session.add(user)
    return user


#получение пользователя по id
async def get_user(session: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


#получение пользователя по name
async def get_by_name(session: AsyncSession, name: str) -> User | None:
    stmt = select(User).where(User.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


#обновление пароля пользователя
@commit
async def update_pass(session: AsyncSession, user_id: int, new_passhash: str, new_sault: str) -> bool:
    stmt = update(User).where(User.id == user_id).values(pass_hash = new_passhash, pass_sault = new_sault)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True


#изменение имени пользователя
@commit
async def update_name(session: AsyncSession, user_id: int, new_name: str) -> bool:
    stmt = update(User).where(User.id == user_id).values(name = new_name)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True


@commit
#удаление пользователя по id
async def del_user(session: AsyncSession, user_id: int) -> bool:
    stmt = delete(User).where(User.id == user_id)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True
