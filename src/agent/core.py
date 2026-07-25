"""
Agent class: owns the LLM client, tool registry, conversation state,
and the tool-calling loop with human-in-the-loop confirmation for
dangerous actions.
"""
import json
from models.llm import LLMClient
from tools import build_tool_registry

SYSTEM_PROMPT = """You are a helpful command-line AI agent.
You can answer questions directly, search the web, and manipulate files
or run commands via tools. Always prefer using tools when a task requires
current information, file access, or command execution. Be concise.
"""

SYSTEM_MESSAGE = {"role": "system", "content": SYSTEM_PROMPT}


class Agent:
    def __init__(self):
        self.llm = LLMClient()
        self.tool_registry = build_tool_registry()
        self.messages = [SYSTEM_MESSAGE]

    def _confirm(self, tool_name: str, args: dict) -> bool:
        """
        get user approval if tool is dangerious
        """
        print(f"\n[CONFIRM] Agent wants to run tool: {tool_name}")
        print(f"          args: {json.dumps(args, indent=2)}")
        answer = input("Proceed? (yes/no): ").strip().lower()
        return answer in ("y", "yes")

    def _execute_tool(self, name: str, args: dict) -> str:
        tool = self.tool_registry.get(name)

        if tool.dangerous:
            if not self._confirm(name, args):
                return "User declined to run this tool."

        try:
            return str(tool.func(**args))
        except Exception as e:
            return f"Tool execution error: {e}"

    def step(self, user_input: str) -> str:
        """
        send user prompt to llm and Loop until the model returns a plain answer (no more tool calls)
        """
        self.messages.append({"role": "user", "content": user_input})

        while True:
            message = self.llm.chat(
                self.messages,
                tools=self.tool_registry.as_openai_schema(),
            )

            # Append assistant message (with tool_calls if present)
            self.messages.append(message.model_dump(exclude_unset=True))

            if not message.tool_calls:
                return message.content or ""

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                result = self._execute_tool(name, args)

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
            # loop again so the model can react to tool results
