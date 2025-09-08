from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv
import motor.motor_asyncio
import uuid
from datetime import datetime
from models.chat import ChatRequest, ChatResponse
from routers.chat import chat_router
from routers.documents import documentRouter


load_dotenv()

app = FastAPI(title="ChatBot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DBNAME = os.getenv("MONGODB_DBNAME")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL
)  # connecting asynchronously to the MongoDB database allowing servicing other users
database = client[MONGODB_DBNAME]

chat_collection = database.chat_sessions
document_chunks_collection = database.document_chunks


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(chat_router)
app.include_router(documentRouter)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
