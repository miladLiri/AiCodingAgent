from typing import Callable
from langchain.tools import BaseTool

class ToolExecutionGuard:
    def __init__(self):
        self._dangerous = set()

    def register_dangerous(self, tool: BaseTool) -> None:
        self._dangerous.add(tool.name)

    def execute(self, tool: BaseTool, *args, **kwargs):
        if not self.__check_and_confirm(tool.name):
            return f"[ABORTED] '{tool.name}' was now allowed by user."
        return tool(*args, **kwargs)

    def __check_and_confirm(self, tool_name: str) -> bool:
        if tool_name not in self._dangerous:
            return True
        answer = input(f"[CONFIRM] '{tool_name}' is a dangerous tool. Proceed? (y/n): ").strip().lower()
        return answer == "y"