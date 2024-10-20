from abc import ABC, abstractmethod


class ABCManager(ABC):
    @abstractmethod
    async def get_key(self, master_key_id: int) -> bytes | None:
        pass

    @abstractmethod
    async def get_current_key(self) -> bytes:
        pass