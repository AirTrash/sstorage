from dotenv import load_dotenv
import os
import asyncio
from io import BytesIO

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv(".env")

from secret_manager.db.models import Base
from secret_manager.db.db_helper import db_helper
from secret_manager.db.crud import users_crud, keys_crud, tokens_crud, secrets_crud

from Cryptodome.Random import get_random_bytes


async def main():
    async with db_helper.engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    key = get_random_bytes(16)
    async with db_helper.sessionmaker() as session:
        #await users_crud.create_user(session, "vasa", "asdffsda", "asdfga")
        #await keys_crud.create_key(session, 1, key, 10)
        #secret = await secrets_crud.create_secret(
        #    session,
        #    name="hello_world",
        #    user_id=1,
        #    key_id=1,
        #    sec_level=10,
        #    secret=key,
        #    tag=key,
        #    nonce=key,
        #    )
        #print(secret)

        ids = await secrets_crud.get_ids_by_name(session, 1, "hello_world")
        for i in ids:
            print(i)


if __name__ == "__main__":
    asyncio.run(main())
