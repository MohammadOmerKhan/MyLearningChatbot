from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
import uuid
from datetime import datetime
from openai import OpenAI
import os
from REACT import run_react_agent

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


async def generate_session_id():
    return str(uuid.uuid4())


async def get_chat_history(session_id: str, limit: int = 5):
    try:
        from main import chat_collection

        cursor = (
            chat_collection.find({"session_id": session_id})
            .sort("timestamp", 1)  #sort ascending to get chronological order
            .limit(limit * 2)
        )

        messages = await cursor.to_list(length=limit * 2)

        #convert to the format expected by ReAct agent: [[user_msg, ai_msg], ...]
        conversation_history = []
        for msg in messages:
            if "user_message" in msg and "ai_response" in msg:
                conversation_history.append([msg["user_message"], msg["ai_response"]])

        return conversation_history

    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []


async def save_to_database(session_id: str, user_message: str, ai_response: str):
    try:
        from main import chat_collection

        message_doc = {
            "session_id": session_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow(),
        }

        await chat_collection.insert_one(message_doc)
        print(f"Saved message for session {session_id}")

    except Exception as e:
        print(f"Error saving to database: {e}")


async def get_ai_response(user_message: str, session_id: str = None) -> str:
    try:
        #get conversation history directly in the correct format
        conversation_history = []
        if session_id:
            conversation_history = await get_chat_history(session_id)
        
        #use the ReAct agent with conversation history
        response = await run_react_agent(user_message, conversation_history)
        return response

    except Exception as e:
        return f"I'm having trouble right now. You said: '{user_message}'"


@chat_router.post("/send", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest):

    try:
        session_id = chat_request.session_id
        if not session_id:
            session_id = await generate_session_id()

        ai_response = await get_ai_response(chat_request.message, session_id)

        await save_to_database(session_id, chat_request.message, ai_response)

        return ChatResponse(response=ai_response, session_id=session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
