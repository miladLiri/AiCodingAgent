from langchain_core.messages import BaseMessage
from src.memory.base_memory_compressor import BaseMemoryCompressor

class HarnessMemory:
    def __init__(
        self,
        compressor: BaseMemoryCompressor,
    ):
        self.messages: list[BaseMessage] = []
        self._compressor = compressor

    def add(self, message: BaseMessage) -> None:
        self.messages.append(message)
        if self._compressor.need_compression(self.messages):
            self._compressor.compress(self.messages)

    def get(self) -> list[BaseMessage]:
        return self.messages

    def clear(self) -> None:
        self.messages = []
