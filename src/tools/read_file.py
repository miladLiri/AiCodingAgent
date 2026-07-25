from tools.base import Tool

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    
TOOL = Tool(
    name="read_file",
    description="Read the contents of a file.",
    parameters={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    func=read_file,
    dangerous=False,
)