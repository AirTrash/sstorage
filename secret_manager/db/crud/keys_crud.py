from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from secret_manager.db.models import Key
from .decorators import commit
from sqlalchemy import select, delete


#id
#master_key_id
#key
#create_date
#end_date

#создает новый ключ, term - срок действия в днях
@commit
async def create_key(session: AsyncSession, master_key_id: int, key: bytes, term: int):
    key = Key(
        master_key_id=master_key_id,
        key=key,
        end_date=datetime.now() + timedelta(days=term)
    )
    session.add(key)
    return key


#возвращает ключ по id
async def get_key(session: AsyncSession, key_id: int) -> Key | None:
    stmt = select(Key).where(Key.id == key_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


#удаляет ключ по id
@commit
async def del_key(session: AsyncSession, key_id: int) -> bool:
    stmt = delete(Key).where(Key.id == key_id)
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return False
    return True
