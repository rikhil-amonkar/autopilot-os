from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from .mail_tool import prompt_user, list_unread_emails, summarize_email

# * Instance of app
app = FastAPI()

# * Define origin routes to allow access to
origins = [
    "http://localhost:5173"  # Dev server
]

# * CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# * Base model for email
class Email(BaseModel):
    email_id: Optional[str] = None
    
# * Base model for prompt
class Prompt(BaseModel):
    message: str  # Required to run model
    
# * Home page
@app.get("/")
def root():
    return {"message": "Welcome to AutoPilot OS!"}

# * List unread emails
@app.get("/emails/unread/")
def view_unread_emails(limit: Optional[int] = 10):  # Query parameter
    unread_emails = list_unread_emails.invoke({"limit": limit})  # Call list tool
    
    # * Validate list
    if not unread_emails:
        raise HTTPException(status_code=404, detail="Could not fetch emails.")
    return unread_emails

# * Summarize emails
@app.get("/emails/{email_id}/summary/")
def view_email_summary(email_id: str):
    email_summary = summarize_email.invoke({"email_id": email_id})  # Call summarize tool
    
    # * Validate summary
    if not email_summary:
        raise HTTPException(status_code=404, detail="Could not create summary.")
    return email_summary

# * Agent (LLM) endpoint
@app.post("/emails/agent/")
def call_agent(request: Prompt):  # Request body
    answer = prompt_user(request.message)  # Call LLM agent

    # * Validate agent
    if not answer:
        raise HTTPException(status_code=404, detail="Could not find answer.")
    return {"response": answer}  # Return as JSON

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run app on local server


