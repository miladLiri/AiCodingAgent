from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain.tools import BaseTool
from src.config import *

class HarnessLLM:
    def __init__(self, tools: list[BaseTool]):
        self._client = ChatOpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            model=MODEL_NAME,
            temperature=0.7
        )
        if tools:
            self._client = self._client.bind_tools(tools)
    
    def invoke(self, messages) -> AIMessage:
        """Invoke the LLM and return LangChain AIMessage."""
        return self._client.invoke(messages)
    
    @property
    def client(self):
        """Access to underlying ChatOpenAI client."""
        return self._client
