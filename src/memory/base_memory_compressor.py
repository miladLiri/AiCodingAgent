from abc import ABC, abstractmethod
from langchain_core.messages import BaseMessage

class BaseMemoryCompressor(ABC):

    @abstractmethod
    def need_compression(self, messages: list[BaseMessage]) -> bool:
        pass

    @abstractmethod
    def compress(self, messages: list[BaseMessage]) -> None:
        pass

    