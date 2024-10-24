from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from secret_manager.db.db_helper import db_helper


async def db_session() -> AsyncSession:
    async with db_helper.get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(db_session)]