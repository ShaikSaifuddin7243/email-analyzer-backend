from fastapi import FastAPI
import os 
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import sys
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGO_URI"))

db = client['email_analyzer']
collection = db['emails']

@app.get("/")
def read_root():
    return {"Hello": "The Email Analyzer API is running!"}

@app.get("/api/emails")
def get_emails():
    emails_from_db = list(collection.find({}, {"_id": 0}))
    return {
        "total_emails": len(emails_from_db),
        "emails": emails_from_db
    }

@app.get("/api/sync")
def sync_emails():
    try:
        subprocess.run([sys.executable, "email_reader.py"], check=True)
        return {"status": "success", "message": "New emails fetched successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}