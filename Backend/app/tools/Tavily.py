from langchain_tavily import TavilySearch

# Initialize the official Tavily Search tool
tavily_tool = TavilySearch(
    max_results=5,
    topic="general",
    include_answer=True,
    search_depth="basic"
)
