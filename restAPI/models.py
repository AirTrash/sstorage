from typing import List, Literal, Annotated
from pydantic import BaseModel
from fastapi import File
from secret_manager.permissions import all_perms


class ErrorMsg(BaseModel):
    message: str
    description: str | None = None


class User(BaseModel):
    name: str
    password: str


class RenameUser(BaseModel):
    old_name: str
    password: str
    new_name: str


class ChangePassword(BaseModel):
    name: str
    old_password: str
    new_password: str


class BaseCreateToken(BaseModel):
    sec_level: int
    permissions: List[Literal[*all_perms]]


class CreateLoginAuth(BaseCreateToken):
    user: User


class CreateTokenAuth(BaseCreateToken):
    token: str


class DelToken(BaseModel):
    token: str
    token_for_del: str


class TokenResp(BaseModel):
    message: str = "success"
    token: str


class StringSecret(BaseModel):
    secret: str
    name: str
    sec_level: int


class BytesSecret(BaseModel):
    secret: Annotated[bytes, File()]
    name: str
    sec_level: int


class Secret(BaseModel):
    secret: str | Annotated[bytes, File()]
    datatype: Literal["str", "bytes"]
    name: str
    sec_level: int


class SecretIdResp(BaseModel):
    secret_id: int
