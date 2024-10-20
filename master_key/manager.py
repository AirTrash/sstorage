import os
from base64 import b64decode, b64encode
from .abc_manager import ABCManager


class MasterKeyManager(ABCManager):
    def __init__(self):
        self.keys = []
        self.load_keys()


    def load_keys(self):
        print("загрузка ключей из", os.getenv("MASTER_KEYS_PATH"))
        with open(os.getenv("MASTER_KEYS_PATH"), "r") as file:
            for line in file:
                if line == "": continue
                key = line.replace("\n", "").replace("\r", "")
                key = b64decode(key.encode("UTF-8"))
                self.keys.append(key)
        print("ключи загружены")


    async def get_key(self, master_key_id: int):
        if len(self.keys) < master_key_id:
            return None
        return self.keys[master_key_id - 1]


    async def get_current_key(self) -> (int, bytes):
        return len(self.keys), self.keys[len(self.keys) - 1]


master_key_manager = MasterKeyManager()
