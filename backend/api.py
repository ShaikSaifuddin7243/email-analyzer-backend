from fastapi import FastAPI
import os 
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("Mongo_URI"))

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