import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class DBhelper:
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url)
        self.sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)


db_helper = DBhelper(os.getenv("DATABASE_URL"))
