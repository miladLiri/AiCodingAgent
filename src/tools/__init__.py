from tools.base import ToolRegistry
from tools.web_search import TOOL as web_search_tool
from tools.write_file import TOOL as write_file_tool
from tools.read_file import TOOL as read_file_tool
from tools.edit_file import TOOL as edit_file_tool
from tools.list_files import TOOL as list_files_tool
from tools.run_command import TOOL as run_command_tool

def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(web_search_tool)
    registry.register(write_file_tool)
    registry.register(read_file_tool)
    registry.register(edit_file_tool)
    registry.register(list_files_tool)
    registry.register(run_command_tool)

    return registry
