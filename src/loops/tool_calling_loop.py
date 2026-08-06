from langchain_core.messages import ToolMessage, AIMessage, ToolCall
from memory.harness_memory import AgentMemory
from src.tools.common.tool_execution_guard import ToolExecutionGuard
from src.tools.common.tool_registry import ToolRegistry
from src.llms.harness_llm import HarnessLLM
from langchain.tools import BaseTool



class ToolCallingLoop:
    def __init__(
        self,
        harness_llm: HarnessLLM,
        tool_registry: ToolRegistry,
        memory: AgentMemory,
        tool_execution_guard: ToolExecutionGuard,
    ):
        self.tool_registry = tool_registry
        self.harness_llm = harness_llm
        self.memory = memory
        self.tool_execution_guard = tool_execution_guard

    def run(self, ai_message : AIMessage) -> AIMessage:

        if not ai_message.tool_calls:
            return ai_message

        while True:

            for tool_call in ai_message.tool_calls:

                tool: BaseTool = self.tool_registry.get(tool_call.name)
                tool_call_result: str = self.tool_execution_guard.execute(tool, tool_call.args)
                tool_message = ToolMessage(content=tool_call_result, tool_call_id= tool_call.id)
                self.memory.add(tool_message)

            ai_message : AIMessage = self.harness_llm.invoke(self.memory.get())
            self.memory.add(ai_message)

            if not ai_message.tool_calls:
                return ai_message

        
       
