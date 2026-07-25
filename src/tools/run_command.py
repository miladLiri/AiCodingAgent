"""
Executes a shell command / script. Always dangerous — must be
confirmed by a human before running.
"""
from tools.base import Tool
import subprocess


def run_command(cmd: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = f"exit_code: {result.returncode}\n"
        if result.stdout:
            output += f"stdout:\n{result.stdout}\n"
        if result.stderr:
            output += f"stderr:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"


TOOL = Tool(
    name="run_command",
    description="Run a shell command or execute a script. Requires human confirmation.",
    parameters={
        "type": "object",
        "properties": {
            "cmd": {"type": "string", "description": "The shell command to run."},
            "timeout": {"type": "integer", "default": 30},
        },
        "required": ["cmd"],
    },
    func=run_command,
    dangerous=True,
)