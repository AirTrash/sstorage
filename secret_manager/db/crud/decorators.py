from typing import Any
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession


#автоматический коммит, принимает сессию как первый аргумент и передает декарируемой функции
#принимает commit как непозиционный аргумент
#возвращяет возвращяемое значение декорируемой функции
def commit(func) -> Any:
    @wraps(func)
    async def wrapper(session: AsyncSession, *args, commit=True, **kwargs):
        ret = await func(session, *args, **kwargs)
        if commit:
            await session.commit()
        return ret
    return wrapper
