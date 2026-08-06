
from src.memory.base_memory_compressor import BaseMemoryCompressor
from src.memory.memory_compressor_llm import MemoryCompressorLLM
from langchain_core.messages import BaseMessage

class RollingSummaryCompressor(BaseMemoryCompressor):
    def __init__(
            self, 
            llm: MemoryCompressorLLM,
            max_messages: int = 20,
            compress_to: int = 5):
        self._llm = llm
        self._max = max_messages
        self._compress_to = compress_to

    
    def need_compression(self, messages: list[BaseMessage]) -> bool:
        return len(messages) > self._max
    
    def compress(self, messages: list[BaseMessage]) -> None:
        recent = messages[-self._compress_to:]
        older = messages[:-self._compress_to]
        summary = self._llm.summarize(older)
        messages = [summary, *recent]