from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import motor.motor_asyncio


sheets_router = APIRouter(prefix="/sheets", tags=["Sheets Data"])


load_dotenv() 

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DBNAME = os.getenv("MONGODB_DBNAME")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL
)  # connecting asynchronously to the MongoDB database allowing servicing other users
database = client[MONGODB_DBNAME]

sheets_data_collection = database.sheets_data


@sheets_router.post("/store")
async def store_json_data(request: Request):
    """Store JSON data from n8n webhook"""
    try:
        # Get the JSON data
        json_data = await request.json()

        # Create a simple data entry
        data_entry = {
            "sheet_id": json_data["sheet_id"],
            "title": json_data["title"],
            "ssId": json_data["ssId"],
            "timestamp": datetime.now(),
        }

        # Store it
        await sheets_data_collection.insert_one(data_entry)

        print(f"Data stored successfully: {data_entry}")
        return {"success": True, "sheet_id": data_entry["sheet_id"], "title": data_entry["title"], "ssId": data_entry["ssId"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@sheets_router.get("/retrieve/{title}")
async def get_specific_data(title: str):
    """Get specific data by title"""

    try:
         item = await sheets_data_collection.find_one({"title":title})

         if item:
            return {
                "Success": True,
                "sheet_id":item["sheet_id"],
                "title":item["title"],
                "ssId":item["ssId"]
            }

         else:
                raise HTTPException(status_code=404, detail="Data not found")

    except Exception as e:        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



    """for item in sheets_data_collection.find():
        if item["title"] == title:
            return {"success": True, "sheet_id": item["sheet_id"], "title": item["title"], "ssId": item["ssId"]}

    raise HTTPException(status_code=404, detail="Data not found")"""
