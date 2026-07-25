"""
Central place to register tools and build the OpenAI-compatible
function schema list automatically.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List


@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]   # JSON schema for the function's args
    func: Callable
    dangerous: bool = False       # requires human confirmation if True


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def as_openai_schema(self) -> List[dict]:
        schema = []
        for tool in self._tools.values():
            schema.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            })
        return schema

    def all(self):
        return self._tools.values()
