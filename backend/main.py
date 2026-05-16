from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai import generate_blog
from devto import post_to_platform
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LeetLog AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Problem(BaseModel):
    title: str
    description: str
    code: str
    author: str = "Anonymous Developer"
    client_time: str = None  # Optional client time string


@app.get("/")
def health_check():
    return {"status": "ok", "message": "LeetLog AI backend is running."}


@app.post("/generate-blog")
def create_blog(problem: Problem):
    """
    Accepts a LeetCode problem (title, description, code) and:
    1. Generates a well-structured blog post using Gemini AI.
    2. Publishes the post directly to Dev.to.
    """
    if not problem.code or problem.code.strip() == "":
        return {"status": "error", "message": "Code is empty, cannot generate blog."}

    try:
        blog_content = generate_blog(problem)
    except Exception as e:
        return {"status": "error", "message": f"Gemini API failure: {str(e)}"}

    try:
        response = post_to_platform(problem.title, blog_content)
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": f"Dev.to API failure: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from twilio.rest import Client
import motor.motor_asyncio

# Twilio setup
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# MongoDB setup
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = mongo_client.leetcodeai

class ReminderPreference(BaseModel):
    whatsapp_number: str
    reminder_time: str = "09:00"
    timezone: str = "Asia/Kolkata"
    is_opted_in: bool = True

@app.post("/reminder/subscribe")
async def subscribe(pref: ReminderPreference):
    await db.preferences.update_one(
        {"whatsapp_number": pref.whatsapp_number},
        {"$set": pref.dict()},
        upsert=True
    )
    return {"status": "success", "message": "Subscribed!"}

@app.post("/reminder/unsubscribe")
async def unsubscribe(data: dict):
    await db.preferences.update_one(
        {"whatsapp_number": data["whatsapp_number"]},
        {"$set": {"is_opted_in": False}}
    )
    return {"status": "success", "message": "Unsubscribed!"}