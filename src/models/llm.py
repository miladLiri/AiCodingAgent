"""
Abstraction over the OpenAI API so other adapters (Anthropic, local, etc.)
can be added later without touching agent/core.py.
"""
from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, MODEL_NAME


class LLMClient:
    def __init__(self, model: str = MODEL_NAME):
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self.model = model

    def chat(self, messages: list, tools: list = None, tool_choice="auto"):
        """
        Sends a chat completion request. Returns the raw message object
        (may contain tool_calls or content).
        """
        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message
