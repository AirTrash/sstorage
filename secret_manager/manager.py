from master_key.manager import master_key_manager
from master_key.abc_manager import ABCManager


class SecretManager:
    def __init__(self, mk_manager: ABCManager):
        self.mk_manager = mk_manager





secret_manager = SecretManager(master_key_manager)
