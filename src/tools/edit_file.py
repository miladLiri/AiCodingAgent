from src.tools.base import Tool

def edit_file(path: str, old_content: str, new_content: str) -> str:
    """
    Simple find-and-replace based edit. old_content must match
    exactly once in the file (like a diff patch anchor).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()

        if old_content not in data:
            return f"Error: old_content not found in {path}"

        count = data.count(old_content)
        if count > 1:
            return f"Error: old_content matches {count} times, must be unique"

        data = data.replace(old_content, new_content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
        return f"Edited {path} successfully"
    except Exception as e:
        return f"Error editing file: {e}"
    

TOOL = Tool(
    name= "edit_file",
    description= "Edit an existing file by replacing old_content with new_content. old_content must uniquely match a substring of the file.",
    parameters= {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "old_content": {"type": "string", "description": "Exact text to find and replace."},
            "new_content": {"type": "string", "description": "Replacement text."},
        },
        "required": ["path", "old_content", "new_content"],
    },
    func=edit_file,
    dangerous= True,
)