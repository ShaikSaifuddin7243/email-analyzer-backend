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

import os

@app.get("/api/sync")
def sync_emails():
    try:
        
        script_path = os.path.join(os.path.dirname(__file__), "email_reader.py")
        
      
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return {"status": "success", "message": "New emails fetched successfully!"}
        
    except subprocess.CalledProcessError as e:
        error_details = e.stderr if e.stderr else str(e)
        return {"status": "error", "message": f"Script crashed: {error_details}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}