from src.config import *
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

class MemoryCompressorLLM:
    def __init__(self):
        self._llm = ChatOpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            model=MODEL_NAME,
        )

    def summarize(self, messages: list[BaseMessage]) -> str:
        history = "\n".join(f"{m.__class__.__name__}: {m.content}" for m in messages)
        response = self._llm.invoke([
            SystemMessage(content="Summarize the following conversation history concisely."),
            HumanMessage(content=history),
        ])
        return response.content