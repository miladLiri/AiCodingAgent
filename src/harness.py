from src.memory.memory_compressor_llm import MemoryCompressorLLM
from src.memory.compression_strategies.rolling_summery_compressor import RollingSummaryCompressor
from src.memory.harness_memory import HarnessMemory
from src.tools.common.tool_registry import ToolRegistry
from src.tools.common.tool_execution_guard import ToolExecutionGuard
from src.tools.read_file import read_file
from src.tools.create_diagram import create_diagram
from src.llms.harness_llm import HarnessLLM
from src.loops.tool_calling_loop import ToolCallingLoop
from src.loops.conversation_loop import ConversationLoop

class Harness:

    def __init__(self):

        #memory
        memory_compressor_llm = MemoryCompressorLLM()
        rolling_summary_compressor = RollingSummaryCompressor(llm=memory_compressor_llm)
        agent_memory = HarnessMemory(compressor=rolling_summary_compressor)

        #tools
        tool_registry = ToolRegistry()
        tool_execution_guard = ToolExecutionGuard()

        tool_registry.register(read_file)
        tool_registry.register(create_diagram)
        tool_execution_guard.register_dangerous(read_file)

        #llm
        harness_llm = HarnessLLM(tools = tool_registry.all())

        #loops
        tool_calling_loop = ToolCallingLoop(
            tool_registry=tool_registry,
            harness_llm=harness_llm,
            memory=agent_memory,
            tool_execution_guard=tool_execution_guard
        )

        self.conversation_loop = ConversationLoop(
            tool_calling_loop=tool_calling_loop,
            harness_llm=harness_llm,
            memory=agent_memory
        )


    def run(self):
        self.conversation_loop.run()
