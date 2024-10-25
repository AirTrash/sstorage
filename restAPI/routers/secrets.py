from typing import Annotated

from fastapi import APIRouter, Response, Body
import logging

from sqlalchemy.ext.horizontal_shard import ShardedSession

from restAPI.dependencies import SessionDep

from restAPI.models import ErrorMsg, SecretIdResp, StringSecret, BytesSecret, Secret
from secret_manager.errors import ServError, PermError

from secret_manager.manager import secret_manager


router = APIRouter(
    prefix="/secrets",
    tags=["secrets"],
    responses={404: {"description": "Not found"}, 201: {"model": SecretIdResp}, 202: {"model": ErrorMsg}, 500: {"description": "unknown error"}}
)


@router.post("/create_string", status_code=201)
async def create_string(session: SessionDep, secret: StringSecret, token: Annotated[str, Body()], resp: Response):
    try:
        secret_id = await secret_manager.create_secret_str(
            session, token, secret.name, secret.sec_level, secret.secret
        )
        return SecretIdResp(secret_id=secret_id)
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        resp.status_code = 500
        logging.error(f"неизвестная ошибка при создании секрета типа str, текст ошибки: {e}")
        return ErrorMsg


@router.post("create_bytes", status_code=201)
async def create_bytes(session: SessionDep, secret: BytesSecret, token: Annotated[str, Body()], resp: Response):
    try:
        secret_id = await secret_manager.create_secret_bytes(
            session, token, secret.name, secret.secret, secret.secret
        )
        return SecretIdResp(secret_id=secret_id)
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        resp.status_code = 500
        logging.error(f"неизвестная ошибка при создании секрета типа str, текст ошибки: {e}")
        return ErrorMsg


@router.get("/get_secret/{token}/{secret_id}", status_code=200)
async def get_secret(session: SessionDep, token: str, secret_id: int, resp: Response):
    try:
        name, data, datatype, sec_level = await secret_manager.get_secret(
            session, token, secret_id
        )
        return Secret(name=name, secret=data, datatype=datatype, sec_level=sec_level)
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        logging.error(f"произошла неизвестная ошибка при получении секрета, текст ошибки: {e}")
        resp.status_code = 500
        return ErrorMsg(message="неизвестная ошибка при получении секрета")


@router.put("/del_secret/{token}/{secret_id}", status_code=200)
async def del_secret(session: SessionDep, token: str, secret_id: int, resp: Response):
    try:
        await secret_manager.del_secret(session, token, secret_id)
        return "success"
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        resp.status_code = 500
        logging.debug(f"произошла неизвестная ошибка при попытке удалить секрет, текст ошибки: {e.message}")
        return ErrorMsg(message="неизвестная ошибка при удалении секрета")
