from dotenv import load_dotenv
import os
import asyncio
from io import BytesIO

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv(".env")

from secret_manager.db.models import Base
from secret_manager.db.db_helper import db_helper
from secret_manager.db.crud import users_crud, keys_crud, tokens_crud, secrets_crud
from secret_manager.permissions import Permissions

from secret_manager.manager import secret_manager

from Cryptodome.Random import get_random_bytes


async def main():
    async with db_helper.engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        #await conn.run_sync(Base.metadata.create_all)
        pass

    async with db_helper.sessionmaker() as session:
        #await secret_manager.create_user(session, "kishaolo", "parol")
        #token1 = await secret_manager.create_token_login_auth(
        #    session,
        #    username="kishaolo",
        #    password="parol",
        #    sec_level=9,
        #    permissions=[Permissions.create_tokens, Permissions.read_secrets]
        #)

        #print(token1)

        #token2 = await secret_manager.create_token_token_auth(
        #    session,
        #    token="YFhjko2gWYX268h8pSXn0Mn4I73uoEP6WcNebC8yA_c",
        #    sec_level=9,
        #    permissions=[Permissions.create_secrets, Permissions.read_secrets]
        #)

        #print(token2)

        ##создание секрета
        #secret = await secret_manager.create_secret_str(
        #    session,
        #    "1_u32r2TAaYBXZ7eMpjo6uCV3QkULYcOo6DiLPYUq3k",
        #    "test1",
        #    9,
        #    "hello world"
        #)
        #print(secret) # возвращает id секрета

        #прочтение секрета уровень безопасности не позволит, т.к. у секрета 10 а у токена 9
        data = await secret_manager.get_secret(session, "1_u32r2TAaYBXZ7eMpjo6uCV3QkULYcOo6DiLPYUq3k", 1)
        print(data)


if __name__ == "__main__":
    asyncio.run(main())
