from .abc_manager import ABCManager


class MasterKeyManager(ABCManager):
    def __init__(self):
        self.keys = []
        self.init_keys()


    def init_keys(self) -> None:
        print("инициализация мастер ключей")
        i = 1
        while True:
            key = input(f"Введите мастер ключ N{i} или нажмите Enter для окончания ввода ключей: ")
            if key == "":
                if len(self.keys) != 0: break
                print("Введите хотя-бы 1 ключ")
                continue
            self.keys.append(key.encode("UTF-8"))
            i += 1


    async def get_key(self, master_key_id: int):
        if len(self.keys) < master_key_id:
            return None
        return self.keys[master_key_id - 1]


    async def get_current_key(self) -> (int, bytes):
        return len(self.keys), self.keys[len(self.keys) - 1]


master_key_manager = MasterKeyManager()
