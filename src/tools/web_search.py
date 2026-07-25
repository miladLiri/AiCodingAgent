"""
Web search tool. Uses Tavily (simple, LLM-friendly search API).
Swap the implementation freely; the interface stays the same.
"""
import requests
from tools.base import Tool
from config import SEARCH_API_KEY


def web_search(query: str, max_results: int = 5) -> str:
    if not SEARCH_API_KEY:
        return "Error: SEARCH_API_KEY not configured."

    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": SEARCH_API_KEY,
                "query": query,
                "max_results": max_results,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return "No results found."

        formatted = []
        for r in results:
            formatted.append(f"- {r.get('title')}\n  {r.get('url')}\n  {r.get('content', '')[:300]}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search error: {e}"


TOOL = Tool(
    name="web_search",
    description="Search the web for current or external information.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query."},
            "max_results": {"type": "integer", "description": "Number of results to return.", "default": 5},
        },
        "required": ["query"],
    },
    func=web_search,
    dangerous=False,
)
