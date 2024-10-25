from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from base64 import b64encode
from secrets import token_hex, compare_digest, token_urlsafe
from hashlib import sha256

from Cryptodome.Random import get_random_bytes

from datetime import datetime
import logging

from . import crypto
from .errors import UserNotFound, IncorrectPass, CannotCreate, TokenNotFound, NotEnoughPerms, CannotGet, DecryptError, \
    SecLevelNotEnought, AccessError, ServError, TargetTokenNotFound
from .permissions import Permissions

from master_key.manager import master_key_manager
from master_key.abc_manager import ABCManager

from secret_manager.db.models import User, Key, Token, Secret
from secret_manager.db.crud import users_crud, tokens_crud, secrets_crud, keys_crud


class SecretManager:
    def __init__(self, mk_manager: ABCManager):
        self.mk_manager = mk_manager


    def __get_passhash(self, password: str, sault: str) -> str:
        string = b64encode(password.encode("UTF-8")).decode("UTF-8") + sault
        return sha256(string.encode("UTF-8")).hexdigest()


    #создает пользователя
    async def create_user(self, session: AsyncSession, username: str, password: str, commit: bool = True) -> bool:
        """
        :param session:
        :param username: имя пользователя в UTF-8
        :param password: пароль в UTF-8
        :param commit: автоматический коммит
        :return: True - если пользователь создан, False - если имя занято.
        """
        user = await users_crud.get_by_name(session, username)
        if user is not None:
            return False
        sault = token_hex(8)
        pass_hash = self.__get_passhash(password, sault)
        await users_crud.create_user(session, username, pass_hash, sault, commit=commit)
        return True


    #проверяет пароль, и возвращает пользователя, использовать для проверки пароля
    async def get_user(self, session: AsyncSession, name: str, password: str) -> User:
        """
        :param session:
        :param name: имя пользователя
        :param password: пароль пользователя
        :return: True если пользователь найден и пароль совпадает, иначе False
        """
        user = await users_crud.get_by_name(session, name)
        if user is None:
            raise UserNotFound(name)
        pass_hash = self.__get_passhash(password, user.pass_sault)
        if not compare_digest(user.pass_hash, pass_hash):
            logging.warning(f"был передан неверный пароль для пользователя {name}")
            raise IncorrectPass(name)
        return user


    #изменить имя пользователя
    async def rename_user(self, session: AsyncSession, name: str, password: str, new_name: str):
        """
        :param session:
        :param name: имя пользователя
        :param password: пароль пользователя
        :param new_name: новое имя пользователя
        :return: True - если удалось, иначе False
        """
        user = await self.get_user(session, name, password)
        updated = await users_crud.update_name(session, user.id, new_name)
        if updated is not True:
            logging.error(f"не удалось сменить имя пользователя {name}")
            raise ServError("ошибка на стороне сервера, не удалось сменить имя")


    #изменить пароль пользователя
    async def change_password(self, session: AsyncSession, name: str, old_password: str, new_password: str):
        """
        :param session:
        :param name: имя пользователя
        :param old_password: старый пароль
        :param new_password: новый пароль
        :return: True - если успешно, иначе False
        """
        user = await self.get_user(session, name, old_password)
        sault = token_hex(8)
        pass_hash = self.__get_passhash(new_password, sault)
        updated = await users_crud.update_pass(session, user.id, pass_hash, sault)
        if updated is not True:
            logging.error(f"не удалось сменить пароль пользователя {name}")
            raise ServError("ошибка на стороне сервера, не удалось сменить пароль")


    async def __create_key(self, session: AsyncSession, term: int, commit=True) -> Key:
        key_bytes = get_random_bytes(16)
        mk_id, master_key = await self.mk_manager.get_current_key()
        enc_key, nonce, tag = crypto.encrypt(key_bytes, master_key)
        key = await keys_crud.create_key(session, mk_id, enc_key, nonce, tag, term, commit=commit)
        return key


    async def __create_token(self, session: AsyncSession, user_id: int, key_id: int | None,
                             sec_level: int, permissions: Sequence, commit=True) -> Token:
        while True:
            token = token_urlsafe(32)
            if await tokens_crud.get_token(session, token) is None:
                break
        token = await tokens_crud.create_token(session, token, user_id, key_id, permissions, sec_level, commit=commit)
        return token


    async def __create_new_token(self, session: AsyncSession, user_id: int,
                                 sec_level: int, permissions: Sequence) -> str:
        try:
            if Permissions.create_secrets in permissions:
                new_key = await self.__create_key(session, 30)
                token = await self.__create_token(session, user_id, new_key.id, sec_level, permissions)
            else:
                token = await self.__create_token(session, user_id, None, sec_level, permissions)
            return token.token
        except Exception as e:
            logging.error(f"не удалось создать токен, текст ошибки: {e}")
            await session.rollback()
            raise CannotCreate("токен")


    #создать токен доступа, аутентификация по логину и паролю
    #функция может вызвать rollback транзакции, а так же будет вызван commit
    async def create_token_login_auth(self, session: AsyncSession, username: str, password: str,
                           sec_level: int, permissions: Sequence) -> str:
        """
        :param session:
        :param username: имя пользователя
        :param password: пароль пользователя
        :param sec_level: уровень безопасности токена
        :param permissions: права токена
        :return: токен
        """
        user = await self.get_user(session, username, password)
        token = await self.__create_new_token(session, user.id, sec_level, permissions)
        return token


    #создать токен доступа, используя для аутентификации токен
    #функция может вызвать rollback транзакции, а так же будет вызван commit
    async def create_token_token_auth(self, session: AsyncSession, token: str, sec_level: int, permissions: Sequence) -> str:
        """
        :param session:
        :param token: токен доступа
        :param sec_level: уровень безопасности
        :param permissions: права токена
        :return: Токен
        """
        token = await tokens_crud.get_token(session, token)
        if token is None:
            raise TokenNotFound
        if Permissions.create_tokens not in token.permissions:
            logging.warning(f"попытка создать токен, не имея на то прав user_id: {token.user_id}")
            raise NotEnoughPerms(Permissions.create_tokens)
        if sec_level > token.sec_level:
            raise SecLevelNotEnought
        token = await self.__create_new_token(session, token.user_id, sec_level, permissions)
        return token


    #удалить токен
    async def del_token(self, session: AsyncSession, token: str, token_for_del: str):
        token = await tokens_crud.get_token(session, token)
        if token is None:
            raise TokenNotFound
        if Permissions.delete_tokens not in token.permissions:
            logging.warning(f"попытка удалить токен, не имея на это прав, user_id: {token.user_id}")
            raise NotEnoughPerms(Permissions.delete_tokens)

        token_for_del = await tokens_crud.get_token(session, token_for_del)
        if token_for_del is None:
            raise TargetTokenNotFound
        if token_for_del.sec_level > token.sec_level:
            raise SecLevelNotEnought

        result = await session.delete(token_for_del)
        await session.commit()


    #сменить ключ токена
    async def __change_key(self, session: AsyncSession, token: Token) -> Key | None:
        try:
            new_key = await self.__create_key(session, 30)
            updated = await tokens_crud.update_key(session, token.token, new_key.id)

            if not updated:
                logging.error(f"не удалось обновить ключ для токена, токен: {token.token}")
                await session.rollback()
                return None

        except Exception as e:
            logging.error(f"ошибка при смене ключа токена, текст ошибки: {e}, токен: {token.token}")
            await session.rollback()
            return None

        logging.info(f"был создан новый ключ для токена: {token.token}, id ключа: {new_key.id}")
        return new_key


    #получить ключ по токену
    async def __get_key(self, session: AsyncSession, token: Token) -> Key:
        key = await keys_crud.get_key(session, token.key_id)
        if key is None or key.end_date < datetime.now():
            key = await self.__change_key(session, token)
        if key is None:
            raise CannotGet("ключ шифрования")
        return key


    async def __decrypt_key(self, key: Key) -> bytes:
        master_key = await self.mk_manager.get_key(key.master_key_id)
        if master_key is None:
            logging.error(f"не удалось получить master key, master_key_id: {key.master_key_id}")
            raise DecryptError
        return crypto.decrypt(key.key, master_key, key.nonce, key.tag)


    async def __create_secret(self, session: AsyncSession, token_id: str,
                              secret_name: str, sec_level: int, data: bytes, datatype: str) -> int:
        token = await tokens_crud.get_token(session, token_id)
        if token is None:
            logging.warning(f"попытка создать секрет несуществующим токеном: {token_id}")
            raise TokenNotFound
        if Permissions.create_secrets not in token.permissions:
            logging.warning(f"попытка создать секрет, не имея на это прав, токен: {token.token}")
            raise NotEnoughPerms(Permissions.create_tokens)
        if sec_level > token.sec_level:
            raise SecLevelNotEnought

        #получение ключка, ассоциированного с токеном и его расшифровка
        key = await self.__get_key(session, token)
        dec_key = await self.__decrypt_key(key)

        #зашифровывание данных полученным ключем
        cyphertext, nonce, tag = crypto.encrypt(data, dec_key)
        secret = await secrets_crud.create_secret(session, secret_name, token.user_id, key.id, sec_level, cyphertext, tag, nonce, datatype)
        if secret is None:
            raise CannotCreate("секрет")
        return secret.id


    #создание секрета типа bytes
    async def create_secret_bytes(self, session: AsyncSession, token: str, secret_name: str, sec_level: int, data: bytes) -> int:
        """
        :param session:
        :param token: токен
        :param secret_name: имя секрета, может быть не уникальным
        :param sec_level: уровень безопасности секрета
        :param data: данные
        :return: id секрета в случае успеха, иначе None
        """
        return await self.__create_secret(session, token, secret_name, sec_level, data, "bytes")


    #создание секрета типа str
    async def create_secret_str(self, session: AsyncSession, token: str, secret_name: str, sec_level: int, data: str) -> int:
        """
        :param session:
        :param token: токен
        :param secret_name: имя секрета, может быть не уникальным
        :param sec_level: уровень безопасности секрета
        :param data: данные
        :return: id секрета в случае успеха, иначе None
        """
        return await self.__create_secret(session, token, secret_name, sec_level, data.encode("UTF-8"), "str")


    async def __decrypt_secret(self, session: AsyncSession, secret: Secret) -> bytes:
        key = await keys_crud.get_key(session, secret.key_id)
        if key is None:
            logging.error(f"не удалось получить ключ, key_id: {secret.key_id}")
            raise CannotGet("ключ")

        dec_key = await self.__decrypt_key(key)

        try:
            data = crypto.decrypt(secret.secret, dec_key, secret.nonce, secret.tag)
        except DecryptError:
            logging.critical(f"не удалось расшифровать секрет, секрет или запись таблицы модифицированы, либо не доступен мастер ключ secret_id: {secret.id}")
            raise DecryptError
        return data


    async def __get_secret(self, session: AsyncSession, token: Token, secret_id: int) -> Secret:
        secret = await secrets_crud.get_secret(session, secret_id)
        if secret is None:
            raise CannotGet("секрет")
        if token.user_id != secret.user_id:
            logging.warning(
                f"попытка прочитать секрет не принадлежащий пользователю, токен: {token.token}, secret_id: {secret_id}")
            raise AccessError(f"секрету {secret_id}")
        if token.sec_level < secret.sec_level:
            logging.warning(
                f"попытка прочитать секрет, не имея подходящий уровень безопасности, токен: {token.token}, secret_id: {secret_id}")
            raise SecLevelNotEnought
        return secret


    #плучить секрет по id
    async def get_secret(self, session: AsyncSession, token_str: str, secret_id: int) -> (bytes | str, str, int):
        """
        :param session:
        :param token_str: токен
        :param secret_id: id секрета
        :return: имя секрета, секрет, тип данных секрета, уровень безопасности секрета
        """
        token = await tokens_crud.get_token(session, token_str)
        if token is None:
            logging.warning(f"попытка прочитать секрет несуществующим токеном, token: {token}, secret_id: {secret_id}")
            raise TokenNotFound
        if Permissions.read_secrets not in token.permissions:
            logging.warning(f"попытка прочитать секрет, не имея прав, токен: {token_str}, secret_id: {secret_id}")
            raise NotEnoughPerms(Permissions.read_secrets)

        secret = await self.__get_secret(session, token, secret_id)
        data = await self.__decrypt_secret(session, secret)

        if secret.datatype == "str":
            data = data.decode("UTF-8")
        return secret.name, data, secret.datatype, secret.sec_level


    async def del_secret(self, session: AsyncSession, token_str: str, secret_id: int):
        token = await tokens_crud.get_token(session, token_str)
        if token is None:
            logging.warning(f"попытка прочитать секрет несуществующим токеном, token: {token}, secret_id: {secret_id}")
            raise TokenNotFound
        if Permissions.delete_secrets not in token.permissions:
            logging.warning(f"попытка прочитать секрет, не имея прав, токен: {token_str}, secret_id: {secret_id}")
            raise NotEnoughPerms(Permissions.delete_secrets)

        secret = await self.__get_secret(session, token, secret_id)
        await session.delete(secret)
        await session.commit()


secret_manager = SecretManager(master_key_manager)
