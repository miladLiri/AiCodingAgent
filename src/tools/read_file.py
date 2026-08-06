from pathlib import Path
from langchain.tools import tool


@tool
def read_file(file_path: str) -> str:
    """Read and return the contents of a text file.

    Args:
        file_path: Path to the file to read.
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return f"Error: File not found: {file_path}"
        if not path.is_file():
            return f"Error: Not a file: {file_path}"

        content = path.read_text(encoding="utf-8", errors="replace")
        return content

    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"
