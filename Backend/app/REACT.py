from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv
import os

load_dotenv()


class State(TypedDict):  # TypedDict is a type that defines the structure of the state
    messages: Annotated[
        list, add_messages
    ]  # Annotated is a type that annotates the state with the type of the messages


graph_builder = StateGraph(
    State
)  # StateGraph is a class that creates a graph of the state


llm = init_chat_model("openai:gpt-4o-mini")  # Initialize the chat model


@tool
def rag_search(query: str) -> str:
    """Search documents using RAG for semantically similar content."""
    try:
        from tools.RAG import rag_tool  # get the rag tool from the tools folder
        import asyncio

        results = asyncio.run(
            rag_tool.search_documents(query)
        )  # search the documents for semantically similar document chunks
        return rag_tool.format_results(results)  # format the results
    except Exception as e:
        return f"RAG search error: {str(e)}"


@tool
def web_search(query: str) -> str:
    """Search the web for real-time information using Tavily."""
    try:
        from tools.Tavily import tavily_tool

        results = tavily_tool.invoke({"query": query})

        if not results.get("results"):
            return "No search results found."

        formatted = (
            f"Web search results for: {results.get('query', 'Unknown query')}\n\n"
        )

        if results.get("answer"):
            formatted += f"Answer: {results['answer']}\n\n"

        formatted += "Sources:\n"
        for i, result in enumerate(results.get("results", []), 1):
            formatted += f"{i}. {result.get('title', 'No title')}\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n"
            formatted += f"   Content: {result.get('content', 'No content')[:200]}...\n"
            if result.get("score"):
                formatted += f"   Relevance Score: {result['score']:.2f}\n"
            formatted += "\n"

        if results.get("response_time"):
            formatted += f"Search completed in {results['response_time']}s\n"

        return formatted
    except Exception as e:
        return f"Web search error: {str(e)}"


tools = [rag_search, web_search]  # tools is a list of the tools


llm_with_tools = llm.bind_tools(
    tools
)  # bind_tools is a method that binds the tools to the LLM


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def should_continue(
    state: State,
):  # this function checks if the last message is a tool call
    messages = state["messages"]  # get the messages from the state
    last_message = messages[-1]  # get the last message from the messages
    # If the LLM makes a tool call, then we route to the "tools" node.
    # Otherwise, we stop (reply to the user).
    if (
        last_message.tool_calls
    ):  # if the last message is a tool call, then we route to the "tools" node.
        return "tools"
    else:
        return "end"


def call_tools(state: State):
    messages = state["messages"]
    last_message = messages[-1]

    for (
        tool_call
    ) in (
        last_message.tool_calls
    ):  # for each tool call in the last message, we execute the tool.
        tool_name = tool_call["name"]  # get the name of the tool
        tool_args = tool_call["args"]  # get the arguments of the tool

        # Find and execute the tool
        for (
            tool
        ) in (
            tools
        ):  # for each tool in the tools list, we check if the name of the tool is the same as the name of the tool call.
            if (
                tool.name == tool_name
            ):  # if the name of the tool is the same as the name of the tool call, then we execute the tool.
                try:
                    result = tool.invoke(tool_args)
                    # Use ToolMessage format as per LangGraph docs
                    messages.append(
                        ToolMessage(  # append the result of the tool to the messages list.
                            content=result, tool_call_id=tool_call["id"]
                        )
                    )
                except Exception as e:
                    messages.append(
                        ToolMessage(
                            content=f"Error executing {tool_name}: {str(e)}",
                            tool_call_id=tool_call["id"],
                        )
                    )
                break

    return {"messages": messages}


# Add nodes to the graph
graph_builder.add_node(
    "chatbot", chatbot
)  # chatbot is the node that handles the conversation
graph_builder.add_node("tools", call_tools)  # tools node handles tool execution

# Add edges
graph_builder.add_edge(START, "chatbot")  # connect the start to the chatbot node
graph_builder.add_conditional_edges(
    "chatbot", should_continue, {"tools": "tools", "end": END}
)  # conditional routing from chatbot
graph_builder.add_edge("tools", "chatbot")  # connect tools back to chatbot

graph = graph_builder.compile()  # compile the graph


async def run_react_agent(
    user_message: str, conversation_history: list = None
) -> (
    str
):  # this method runs the ReAct agent with a user message and conversation history
    try:
        # Build messages from conversation history
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {"role": "user", "content": msg[0]}
                )  # index zero because user prompts first
                messages.append(
                    {"role": "assistant", "content": msg[1]}
                )  # index one becuase model responds second

        messages.append(
            {"role": "user", "content": user_message}
        )  # add the current user message

        initial_state = {
            "messages": messages
        }  # setting the initial state with full conversation history
        result = graph.invoke(initial_state)  # invoke the graph with the initial state
        last_message = result["messages"][
            -1
        ]  # get the last message from the result by indexing the messages list
        return last_message.content
    except Exception as e:
        return f"Error running agent: {str(e)}"
