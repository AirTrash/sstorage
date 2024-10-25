from fastapi import APIRouter, Response
import logging

from restAPI.dependencies import SessionDep

from restAPI.models import User, ErrorMsg, RenameUser, ChangePassword
from secret_manager.errors import ServError, PermError

from secret_manager.manager import secret_manager


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}, 202: {"model": ErrorMsg}, 500: {"description": "unknown error"}},
)


@router.post("/create", status_code=201)
async def root(session: SessionDep, user: User, resp: Response):
    try:
        created = await secret_manager.create_user(
            session,
            user.name,
            user.password
        )
        if not created:
            resp.status_code = 202
            return ErrorMsg(message="пользователь с таким именем уже существует")
        return "success"
    except Exception as e:
        logging.error(f"произошла ошибка при обработке запроса на создание пользователя, текст ошибки: {e}")
        resp.status_code = 202
        return ErrorMsg(message="пользователь не был создан")


@router.post("/rename", status_code=202)
async def rename(session: SessionDep, rename_user: RenameUser, resp: Response):
    try:
        await secret_manager.rename_user(
            session,
            rename_user.old_name,
            rename_user.password,
            rename_user.new_name
        )

        resp.status_code = 201
        return "success"
    except (ServError, PermError) as e:
        return ErrorMsg(message=e.message)
    except Exception as e:
        logging.error(f"произошла ошибка при попытке изменить имя пользователя, текст ошибки: {e}")
        resp.status_code = 500
        return ErrorMsg(message="неизвестная ошибка")


@router.post("/change_password", status_code=202)
async def change_password(session: SessionDep, password: ChangePassword, resp: Response):
    try:
        await secret_manager.change_password(
            session, password.name, password.old_password,
            password.new_password
        )
        resp.status_code = 201
        return "success"
    except (ServError, PermError) as e:
        return ErrorMsg(message=e.message)
    except Exception as e:
        logging.error(f"произошла ошибка при попытке изменить пароль, текст ошибки: {e}")
        resp.status_code = 500
        return ErrorMsg(message="неизвестная ошибка")
