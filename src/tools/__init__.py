"""
External Tools Integration
"""
from src.config import Settings

try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults


def initialize_tools():
    """Initialize external tools like Tavily search"""
    tavily_tool = None
    
    if Settings.TAVILY_API_KEY:
        tavily_tool = TavilySearchResults(max_results=3)
        print("[SYSTEM] Tavily search tool initialized.")
    else:
        print("[WARNING] TAVILY_API_KEY not configured. The agent will not have internet access.")
    
    return {"tavily_tool": tavily_tool}
