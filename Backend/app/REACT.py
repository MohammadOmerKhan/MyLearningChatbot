from typing import Literal

from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langfuse import get_client
from langgraph.checkpoint.memory import InMemorySaver
import os
import concurrent.futures
import asyncio

load_dotenv()
langfuse = get_client()

# Initialize LLM
llm = init_chat_model("openai:gpt-4o-mini")
memory = InMemorySaver()


web_search_tool = TavilySearch(max_results=2)


@tool
def rag_search(query: str) -> str:
    """Use for retrieving and comparing information from financial documents in the knowledge base using cosine similarity."""
    try:
        from tools.RAG import rag_tool
        import asyncio

        try:
            # Check if we're already in an event loop
            loop = asyncio.get_running_loop()
            # If we're in a loop, we need to run the async function differently
            import concurrent.futures
            import threading
            
            def run_async_in_thread():
                # Create a new event loop in the thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(rag_tool.search_documents(query))
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                results = future.result()
                
        except RuntimeError:
            # No running loop, we can use asyncio.run directly
            results = asyncio.run(rag_tool.search_documents(query))

        formatted_results = rag_tool.format_results(results)
        return formatted_results

    except Exception as e:
        print(f"RAG search tool error: {e}")
        return f"RAG search tool error: {e}"


tools = [web_search_tool, rag_search]
tools_by_name = {
    tool.name: tool for tool in tools
}  # create a dictionary of the tools by name. Makes it easier to call the tools by name.
llm_with_tools = llm.bind_tools(tools)


def llm_call(state: MessagesState):
    lf_prompt = langfuse.get_prompt("react-agent", type="chat", label="production")
    prompt_template = ChatPromptTemplate.from_messages(lf_prompt.get_langchain_prompt())

    messages = state["messages"]
    last_message = messages[-1]
    user_input = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    # Use the full conversation history, not just the last message
    formatted_messages = prompt_template.format_messages(input=user_input)

    # Add the conversation history to the formatted messages
    # all_messages = list(messages[:-1]) + formatted_messages  # Include all previous messages + formatted prompt

    response = llm_with_tools.invoke(
        [SystemMessage(content="You are a helpful assistant.")] + state["messages"]
    )

    return {"messages": [response]}


def tool_node(state: dict):

    result = []
    for tool_call in state["messages"][-1].tool_calls:  # iterate through the tool calls
        tool = tools_by_name[tool_call["name"]]  # get the tool by name
        observation = tool.invoke(
            tool_call["args"]
        )  # invoke the tool with the arguments
        result.append(
            ToolMessage(content=observation, tool_call_id=tool_call["id"])
        )  # append the tool message to the result
    return {"messages": result}


def should_continue(state: "MessagesState") -> Literal["environment", END]:
    """Decide whether to continue the conversation or end it depending on whether a tool was called"""
    message = state["messages"]
    last_message = message[-1]

    if last_message.tool_calls:  # if a tool was called, continue the conversation
        return "tools"  # return the environment node
    else:
        return END  # if no tool was called, end the conversation


graph_builder = StateGraph(MessagesState)

graph_builder.add_node("llm_call", llm_call)
graph_builder.add_node("environment", tool_node)  # add the tool node to the graph

graph_builder.add_edge(
    START, "llm_call"
)  # add the edge from the start to the llm call node
graph_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tools": "environment",
        END: END,
    },  # add the conditional edges from the llm call node to the environment node where if the tool was called, the conversation continues, otherwise it ends
)

graph_builder.add_edge("environment", "llm_call")

graph = graph_builder.compile(checkpointer=memory)
