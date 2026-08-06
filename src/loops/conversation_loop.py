
from langchain_core.messages import HumanMessage, AIMessage

from memory.harness_memory import HarnessMemory
from src.loops.tool_calling_loop import ToolCallingLoop
from src.llms.harness_llm import HarnessLLM

class ConversationLoop:
    def __init__(
        self,
        harness_llm: HarnessLLM,
        memory: HarnessMemory,
        tool_calling_loop: ToolCallingLoop
    ):
        self.harness_llm = harness_llm
        self.memory = memory
        self.tool_calling_loop = tool_calling_loop
    
    def step(self, user_message: str) -> AIMessage:
       
        human_message = HumanMessage(content=user_message)
        self.memory.add(human_message)
        
        ai_message : AIMessage = self.harness_llm.invoke(self.memory.get_messages())
        self.memory.add(ai_message)
        
        if ai_message.tool_calls:
            ai_message = self.tool_calling_loop.run(ai_message)
        
        return ai_message

    
    def run(self):
        while True:
            user_input = input("prompt: ").strip()
            
            if user_input.lower() == "exit":
                print("Exiting conversation loop.")
                break
            
            if not user_input:
                continue
            
            try:
                ai_message: AIMessage = self.step(user_input)
                print(f"Agent: {ai_message.content}\n")
            except Exception as e:
                print(f"error: {e}\n")
