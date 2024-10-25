from fastapi import APIRouter, Response
import logging

from restAPI.dependencies import SessionDep

from restAPI.models import ErrorMsg, CreateLoginAuth, TokenResp, CreateTokenAuth, DelToken
from secret_manager.errors import ServError, PermError

from secret_manager.manager import secret_manager


router = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
    responses={404: {"description": "Not found"}, 201: {"model": TokenResp}, 202: {"model": ErrorMsg}, 500: {"description": "unknown error"}}
)


@router.post("/create-login-auth", status_code=201)
async def create_login_auth(session: SessionDep, token: CreateLoginAuth, resp: Response):
    try:
        token = await secret_manager.create_token_login_auth(
            session, token.user.name, token.user.password,
            token.sec_level, token.permissions
        )
        return TokenResp(token=token)
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        resp.status_code = 500
        logging.error(f"неизвестная ошибка при создании токена, с аутентификацией по лгину и паролю, текст ошибки: {e}")
        return ErrorMsg(message="неизвестная ошибка при создании токена")


@router.post("/create", status_code=201)
async def create_token_auth(session: SessionDep, token: CreateTokenAuth, resp: Response):
    try:
        token = await secret_manager.create_token_token_auth(
            session, token.token, token.sec_level,
            token.permissions
        )
        return TokenResp(token=token)
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        resp.status_code = 500
        logging.error(f"неизвестная ошибка при создании токена с аутентификацией по токену, текст ошибки: {e}")
        return ErrorMsg(message="неизвестная ошибка при создании токена")


@router.post("/delete", status_code=200)
async def del_token(session: SessionDep, token: DelToken, resp: Response):
    try:
        await secret_manager.del_token(session, token.token, token.token_for_del)
        return "success"
    except (ServError, PermError) as e:
        resp.status_code = 202
        return ErrorMsg(message=e.message)
    except Exception as e:
        resp.status_code = 500
        logging.error(f"неизвестная ошибка при попытке удалить токен, текст ошибки: {e}")
        return ErrorMsg(message="неизвестная ошибка при удалении токена")
