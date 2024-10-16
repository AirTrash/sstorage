from dotenv import load_dotenv
import os
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv(".env")


async def test(sessmaker):
    async with sessmaker() as session:
        print(session)


async def main():
    async with engine.begin() as conn:
        print(conn)


if __name__ == "__main__":
    connect_args = {
    }

    engine = create_async_engine(
        os.getenv("DATABASE_URL"),
        connect_args=connect_args
    )
    print(engine)

    asyncio.run(main())
