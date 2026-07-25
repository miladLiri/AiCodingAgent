import os
from src.tools.base import Tool

def list_files(directory: str = ".") -> str:
    try:
        entries = os.listdir(directory)
        return "\n".join(entries) if entries else "(empty)"
    except Exception as e:
        return f"Error listing files: {e}"
    

TOOL = Tool(
    name="list_files",
    description="List files in a directory.",
    parameters={
        "type": "object",
        "properties": {"directory": {"type": "string", "default": "."}},
        "required": [],
    },
    func=list_files,
    dangerous=False,
)