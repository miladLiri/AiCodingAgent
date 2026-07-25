import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_NAME = os.getenv("AGENT_MODEL", "gpt-4o")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")  # e.g. Tavily / Serper key
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "tavily")