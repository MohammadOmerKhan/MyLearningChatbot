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
import requests
from datetime import datetime
import pytz

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
        
        results = rag_tool.search_documents(query)
        formatted_results = rag_tool.format_results(results)
        return formatted_results

    except Exception as e:
        print(f"RAG search tool error: {e}")
        import traceback

        traceback.print_exc()
        return f"RAG search tool error: {e}"


@tool
def n8n_webhook_email_trigger(message: str, email: str) -> str:
    """Trigger the n8n webhook with a message."""

    try:
        webhook_url = "https://omerkhan.app.n8n.cloud/webhook-test/test-webhook"

        payload = {
            "action": "send_email",
            "message": message,
            "recipient_email": email,
            "subject": "Message from AI Agent",
            "timestamp": str(datetime.now()),
            "source": "ai_agent",
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            return f"Webhook triggered successfully! Response: {response.text}"
        else:
            return f"Webhook error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"n8n webhook error: {str(e)}"


@tool
def n8n_webhook_sheets_trigger(action: str, sheet_name: str, **kwargs) -> str:
    """Trigger the n8n webhook with a sheets data. action is either create_sheet or update_sheet. Set sheet-name to the sheet name the
    user wants to create or update. The data fields are the data fields the user wants to create or update. The key you create will be the column header
    and the value will be the data the user wants to create or update. Do not use this tool for setitng meetings. The n8n_webhook_meeting_trigger is for that.
    """

    try:
        webhook_url = "https://omerkhan.app.n8n.cloud/webhook-test/test-webhook"

        data_fields = dict(kwargs)

        payload = {"action": action, "sheet_name": sheet_name, "data": data_fields}

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            return f"Webhook triggered successfully! Response: {response.text}"
        else:
            return f"Webhook error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"n8n webhook error: {str(e)}"


@tool
def n8n_webhook_meeting_trigger(
    attendee_email: str, start_time: str, end_time: str, location: str
) -> str:
    """Trigger the n8n webhook with data for a meeting. This will be the start and end time of the meeting. The email of the person with whom the meeting is scheduled.
        And the schedule of the meeting. The user will provide the start and end times relevan to the present time. The meeting is always scheduled for some point in
        the future so you must not assume the years, months and days. Use the get_utc_now tool to get the current time and use that as a reference. For n8n’s Google Calendar node,
         the datetime format expected is RFC 3339 / ISO-8601 style. if the user says something like ""schedule a meeting with john doe from 10 am  to 11 am next Tuesday"", you must
          get the current time from the get_utc_now tool and use that as the current time when doing your calculations. For example if it's Monday and the user says ""schedule a meeting with john doe from 10 am  to 11 am next Tuesday"",
          and when you get the current time from the get_utc-now tool and it says the date is the 15th of September, you must schedule the meeting for the 23d of September.
          CRITICAL DATE CALCULATION RULES:
    1. ALWAYS call get_utc_now() first to get current date/time
    2. For "next [day]" calculations:
       - If today is Monday and user says "next Tuesday" → schedule for tomorrow (Tuesday of this week)
       - If today is Tuesday and user says "next Tuesday" → schedule for next week's Tuesday (7 days from now)
       - If today is Wednesday-Sunday and user says "next Tuesday" → schedule for the Tuesday of next week
    3. Calculate the exact date by adding days to current date
    4. Format the final datetime as RFC3339 (YYYY-MM-DDTHH:MM:SSZ)

    Example: If get_utc_now() returns "2024-12-19T14:30:00Z" (Thursday) and user says "next Tuesday 2:30pm",
    calculate: Thursday + 5 days = Tuesday, so use "2024-12-24T14:30:00Z"
    """

    try:
        webhook_url = "https://omerkhan.app.n8n.cloud/webhook-test/test-webhook"

        payload = {
            "action": "meeting",
            "start_time": start_time,
            "end_time": end_time,
            "with": attendee_email,
            "at": location,
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            return f"Webhook triggered successfully! Response: {response.text}"
        else:
            return f"Webhook error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"n8n webhook error: {str(e)}"

    # @tool
    # def get_utc_now() -> str:
    """Get current UTC date and time for meeting scheduling reference."""
    # from datetime import datetime, timezone
    # return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


@tool
def get_utc_now(timezone: str) -> str:
    """Get current UTC date and time in RFC3339 format for meeting scheduling reference."""

    timezone = pytz.timezone(timezone)
    current_time = datetime.now(timezone)

    return current_time.strftime("%Y-%m-%dT%H:%M:%S%z")


@tool
def atlas_db(query: str, response: str, action: str, time: str) -> str:
    """Store or retrieve conversaiton history in the atlas db. Set the action as retrieve or store depending on whats needed. The time parameter is the timestamp of the message.
    The query parameter is the query from the user. The response parameter is the final response from the agent.
    """

    try:
        webhook_url = "https://omerkhan.app.n8n.cloud/webhook-test/test-webhook"

        payload = {
            "action": action,
            "query": query,
            "response": response,
            "time": time,
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            return f"Webhook triggered successfully! Response: {response.text}"
        else:
            return f"Webhook error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"n8n webhook error: {str(e)}"


@tool
def resume_update(job_description: str) -> str:
    """Format the Provided job description text for a n8n webhook. The job_description parameter is the job description from the user. Pass the formatted job description as the parameter to this tool."""

    try:
        webhook_url = "https://omerkhan.app.n8n.cloud/webhook-test/test-webhook"

        payload = {
            "action": "resume_update",
            "job_description": job_description,
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            return f"Webhook triggered successfully! Response: {response.text}"
        else:
            return f"Webhook error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"n8n webhook error: {str(e)}"


tools = [
    rag_search,
    web_search_tool,
    n8n_webhook_email_trigger,
    n8n_webhook_sheets_trigger,
    n8n_webhook_meeting_trigger,
    get_utc_now,
    atlas_db,
    resume_update,
]  # tools is a list of the tools


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
