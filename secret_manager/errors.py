class PermError(Exception):
    def __init__(self, message="недостаточно прав"):
        self.message = message
        self.status_code = 401
        super().__init__(self.message)


class IncorrectPass(PermError):
    def __init__(self, entity: str):
        super().__init__(f"пароль для {entity} не верен")


class NotEnoughPerms(PermError):
    def __init__(self, permissions: str):
        super().__init__(f"не достаточно прав, недостающие права: {permissions}")


class SecLevelNotEnought(PermError):
    def __init__(self):
        super().__init__(f"уровня безопасности токена недостаточно для этой операции")


class AccessError(PermError):
    def __init__(self, entity: str):
        super().__init__(f"у вас нет доступа к {entity}")


class ServError(Exception):
    def __init__(self, message="ошибка на стороне сервера"):
        self.message = message
        super().__init__(self.message)
        self.status_code = 500


class UserNotFound(ServError):
    def __init__(self, username: str):
        super().__init__(f"пользователь {username} не найден")
        self.status_code = 404


class TokenNotFound(ServError):
    def __init__(self):
        super().__init__(f"токен не найден")
        self.status_code = 404


class TargetTokenNotFound(ServError):
    def __init__(self):
        super().__init__(f"целевой токен не найден")
        self.status_code = 404


class CannotCreate(ServError):
    def __init__(self, entity: str):
        super().__init__(f"не удалось создать {entity}")


class CannotGet(ServError):
    def __init__(self, entity: str):
        super().__init__(f"не удалось получить {entity}")
        self.status_code = 404


class CannotUpdate(ServError):
    def __init__(self, entity: str):
        super().__init__(f"не удалось обновить {entity}")


class DecryptError(ServError):
    def __init__(self):
        super().__init__("не удалось расшифровать")


class MaxLimit(ServError):
    def __init__(self, limit: int):
        super().__init__(f"превышен максимальный лимит для получения записей в одном запросе: {limit}")