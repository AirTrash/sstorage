import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy import Column, LargeBinary
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    pass_hash: Mapped[str]
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class Key(Base):
    __tablename__ = "keys"
    id: Mapped[int] = mapped_column(primary_key=True)
    master_key_id: Mapped[int]
    key: Mapped[str]
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    end_date: Mapped[datetime.datetime]


class Token(Base):
    __tablename__ = "tokens"
    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    key_id: Mapped[int] = mapped_column(ForeignKey(Key.id))
    permissions: Mapped[str]


class Secret(Base):
    __tablename__ = "secrets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    key_id: Mapped[int] = mapped_column(ForeignKey(Key.id))
    secret = Column(LargeBinary())
    tag = Column(LargeBinary())
    nonce = Column(LargeBinary())
