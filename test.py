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
        await conn.run_sync(Base.metadata.create_all)

    key = get_random_bytes(16)
    async with db_helper.sessionmaker() as session:
        #user = await secret_manager.create_user(session, "kishaolo", "parol")
        #token = await secret_manager.create_token_login_auth(session, "kishaolo", "parol", 10,
        #                                                     [Permissions.create_secrets, Permissions.create_tokens])

        #token = await secret_manager.create_token_token_auth(session, "Pb6BQSGb7bawLA3v6LDSaB5FWbPQ0A21Iy5aWN_tugY", 10, [Permissions.read_secrets])
        #print(token)
        #secret = await secret_manager.create_secret_str(
        #    session,
        #    "Pb6BQSGb7bawLA3v6LDSaB5FWbPQ0A21Iy5aWN_tugY",
        #    "test1",
        #    10,
        #    "hello"
        #)
        #print(secret)
        data = await secret_manager.get_secret(session, "RGIaLOh9rUh-nGhpacLFZ_6hvCNGPxfprtmencjRfmg", 1)
        print(data)


if __name__ == "__main__":
    asyncio.run(main())
