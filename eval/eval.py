# eval/eval_agent.py

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent.core import Agent
from src.models.llm import LLMClient
from src.tools.base import ToolRegistry
from src.tools.web_search import TOOL as web_search_tool
from src.tools.write_file import TOOL as write_file_tool
from src.tools.read_file import TOOL as read_file_tool
from src.tools.edit_file import TOOL as edit_file_tool
from src.tools.list_files import TOOL as list_files_tool
from src.tools.run_command import TOOL as run_command_tool
from dataclasses import dataclass
from typing import Optional


def make_mock_registry(fs: dict) -> ToolRegistry:
    registry = ToolRegistry()

    def fake_web_search(query: str) -> str:
        return f"[MOCK] Latest React version is 19.0.0 (query: {query})"

    def fake_write_file(path: str, content: str) -> str:
        fs[path] = content
        return f"Wrote {len(content)} bytes to {path}"

    def fake_read_file(path: str) -> str:
        return fs.get(path, f"Error: {path} not found")

    def fake_edit_file(path: str, old_str: str, new_str: str) -> str:
        if path not in fs:
            return f"Error: {path} not found"
        if old_str not in fs[path]:
            return f"Error: string not found in {path}"
        fs[path] = fs[path].replace(old_str, new_str, 1)
        return f"Edited {path}"

    def fake_list_files(directory: str = ".") -> str:
        return "\n".join(fs.keys()) or "(empty)"

    def fake_run_command(command: str) -> str:
        if command.startswith("cat "):
            path = command[4:].strip()
            return fs.get(path, f"cat: {path}: No such file or directory")
        return f"[MOCK RUN] {command}"

    mock_funcs = {
        web_search_tool.name:  fake_web_search,
        write_file_tool.name:  fake_write_file,
        read_file_tool.name:   fake_read_file,
        edit_file_tool.name:   fake_edit_file,
        list_files_tool.name:  fake_list_files,
        run_command_tool.name: fake_run_command,
    }

    for tool in [web_search_tool, write_file_tool, read_file_tool,
                 edit_file_tool, list_files_tool, run_command_tool]:
        registry.register(dataclasses.replace(tool, func=mock_funcs[tool.name]))

    return registry


def make_agent(fs: dict) -> Agent:
    """Build an Agent with a mocked tool registry and auto-approved HITL."""
    registry = make_mock_registry(fs)
    agent = Agent(tool_registry=registry)
    agent._confirm = lambda tool_name, args: True  # auto-approve dangerous tools in eval
    return agent


def extract_tool_call_names(agent: Agent) -> list:
    """Scan agent.messages for assistant tool_calls, in order."""
    names = []
    for msg in agent.messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                names.append(tc["function"]["name"])
    return names


# ---------------------------------------------------------------------------
# Part 1 — single-turn tool choice (one case per registered tool + no-tool)
# ---------------------------------------------------------------------------

@dataclass
class ToolChoiceCase:
    prompt: str
    expected_tool: Optional[str]


TOOL_CHOICE_CASES = [
    ToolChoiceCase("What is 2+2?",                                    None),
    ToolChoiceCase("Search for the latest React version.",           web_search_tool.name),
    ToolChoiceCase("Create hello.txt with content 'hi'.",             write_file_tool.name),
    ToolChoiceCase("Read the contents of hello.txt.",                 read_file_tool.name),
    ToolChoiceCase("In hello.txt replace 'hi' with 'hello'.",         edit_file_tool.name),
    ToolChoiceCase("List all files in the current directory.",        list_files_tool.name),
    ToolChoiceCase("Run the command `echo done` in the shell.",       run_command_tool.name),
]


def run_tool_choice_case(case: ToolChoiceCase) -> dict:
    agent = make_agent({})
    agent.step(case.prompt)
    called = extract_tool_call_names(agent)
    first = called[0] if called else None
    return {"prompt": case.prompt, "expected": case.expected_tool,
            "actual": first, "passed": first == case.expected_tool}


# ---------------------------------------------------------------------------
# Part 2 — multi-turn behavior (a single step() call already runs the
# full tool loop until the model gives a plain answer)
# ---------------------------------------------------------------------------

@dataclass
class BehaviorCase:
    name: str
    prompt: str
    expected_tool_order: list
    judge_question: str


BEHAVIOR_CASES = [
    BehaviorCase(
        name="write_then_run",
        prompt="Create hello.txt containing 'hi', then run `cat hello.txt` and tell me its contents.",
        expected_tool_order=[write_file_tool.name, run_command_tool.name],
        judge_question="Did the assistant correctly report that hello.txt contains 'hi'?",
    ),
    BehaviorCase(
        name="search_then_answer",
        prompt="Search for the latest React version and tell me what it is.",
        expected_tool_order=[web_search_tool.name],
        judge_question="Did the assistant correctly state the latest React version (19.0.0)?",
    ),
]


def _is_subsequence(expected: list, actual: list) -> bool:
    idx = 0
    for tool in actual:
        if idx < len(expected) and tool == expected[idx]:
            idx += 1
    return idx == len(expected)


def llm_judge(question: str, response: str) -> str:
    prompt = (f"Question: {question}\nAgent's response: {response}\n\n"
              "Answer with exactly one word: PASS or FAIL.")
    verdict = LLMClient().complete(prompt).strip().upper()
    return "PASS" if verdict.startswith("PASS") else "FAIL"


def run_behavior_case(case: BehaviorCase) -> dict:
    fs = {}
    agent = make_agent(fs)
    final_answer = agent.step(case.prompt)
    call_log = extract_tool_call_names(agent)
    order_ok = _is_subsequence(case.expected_tool_order, call_log)
    verdict = llm_judge(case.judge_question, final_answer)
    return {"name": case.name, "call_log": call_log, "order_ok": order_ok,
            "final_answer": final_answer, "judge_verdict": verdict,
            "passed": order_ok and verdict == "PASS"}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    print("=" * 60, "\nSINGLE-TURN TOOL CHOICE\n" + "=" * 60)
    tc_results = [run_tool_choice_case(c) for c in TOOL_CHOICE_CASES]
    for r in tc_results:
        print(f"[{'PASS' if r['passed'] else 'FAIL'}] '{r['prompt']}' "
              f"expected={r['expected']} actual={r['actual']}")

    print("\n" + "=" * 60, "\nMULTI-TURN BEHAVIOR\n" + "=" * 60)
    bh_results = [run_behavior_case(c) for c in BEHAVIOR_CASES]
    for r in bh_results:
        print(f"[{'PASS' if r['passed'] else 'FAIL'}] {r['name']}")
        print(f"    order: {r['call_log']} (order_ok={r['order_ok']})")
        print(f"    judge: {r['judge_verdict']}")
        print(f"    answer: {r['final_answer'][:200]}")

    all_results = tc_results + bh_results
    passed = sum(r["passed"] for r in all_results)
    print(f"\nTOTAL: {passed}/{len(all_results)} passed")
    sys.exit(0 if passed == len(all_results) else 1)


if __name__ == "__main__":
    main()