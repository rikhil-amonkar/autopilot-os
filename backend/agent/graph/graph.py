from dotenv import load_dotenv
from typing import TypedDict
import os
import base64
import re
from html import unescape
# from transformers import pipeline

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

load_dotenv()  # Load .env variables

# * Load Google credentials
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN=os.getenv("GOOGLE_REFRESH_TOKEN")
GMAIL_ADDRESS=os.getenv("GMAIL_ADDRESS")

# DEBUG: Validate tokens
# print(f"Token exists: {GOOGLE_REFRESH_TOKEN is not None}")
# print(f"Client ID exists: {GOOGLE_CLIENT_ID is not None}")

# * Define model
CHAT_MODEL = "llama3.2"
BASE_URL = "http://host.docker.internal:11434"  # Default Ollama URL (in Docker)
# LANGUAGE_CLASSIFIER = pipeline("text-classification", model="textattack/bert-base-uncased-CoLA")

# * Scopes for Gmail and Calendar
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar"
]

# * Initialize chat state
class ChatState(TypedDict):
    messages: list
    
"""
GMAIL API GUIDE:

service = connect()  # Returns Gmail API service

# Example Gmail API methods:

service.users().messages().list()           # Get emails
service.users().messages().send()           # Send email
service.users().messages().delete()         # Delete email

# Methods follow REST API pattern: service.resource().action()
"""

# * Connect to inbox
def connect():
    creds = Credentials(
        token=None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES  # Accessible features (email, calendar)
    )
    try:
        creds.refresh(Request())  # Get access token
    except Exception as e:
        print(f"Failed to refresh token: {e}")
    service = build("gmail", "v1", credentials=creds)  # Build API service
    
    return service

# * Return list of unread email content
@tool
def list_unread_emails(limit: int = 10):
    """Collect all emails from the inbox which are classified as "UNREAD" and return their corresponding IDs."""

    print("TOOL CALLED: List Unread Emails")
    
    # * Collect unread emails through API service
    service = connect()
    unread_emails = service.users().messages().list(
        userId="me", 
        q="is:unread",  # Only unread emails (query)
        maxResults=limit  # Limit max query (model can still change)
    ).execute()
    
    # * Validate existance
    if not unread_emails.get("messages"):
        return "You have no unread messages."
    
    # * Extract message IDs
    email_ids = [email["id"] for email in unread_emails.get("messages", [])]
    cleaned_ids = [id.replace("<", "").replace(">", "") for id in email_ids]
    
    print("="*50)
    print("\nHere are your unread emails:\n")
    
    # * Display email list to terminal
    for clean_id in cleaned_ids:
        
        # * Extract email contents
        subject, sender, date, _ = extract_email_info(clean_id)
        
        if subject and sender and date:
            date = date[:25]
            print(f"**ID:** {clean_id} | **Subject:** {subject} | **Date:** {date} | **From:** {sender}")
        else:
            print(f"**ID:** {clean_id} | Not Enough Info")
    
    return cleaned_ids[:limit]
    
# * Convert base64 content to base10 text
def ascii_text_convert(email_content: str):
    
    try:
        # * Check if padding is needed (base64 must be % 4)
        missing_padding = len(email_content) % 4
        if missing_padding:
            email_content += "=" * (4 - missing_padding)
        
        # * Base64 decode the string directly
        dencoded_bytes = base64.b64decode(email_content)
        decoded_email = dencoded_bytes.decode("utf-8", errors="replace")  # Replace unfamiliar characters
        
        return decoded_email
    
    # * Return if email content is already plain text
    except Exception:
        
        return email_content

# * Extract readable text from code content
def extract_text_from_html(code_content: str):
    text = re.sub(r'<[^>]+>', '', code_content)  # Remove html (<, >) tags
    text = unescape(text)  # Convert to standard text
    text = re.sub(r'\{[^}]*\}', '', text)  # Remove CSS ({, }) tags
    text = re.sub(r'\S{30,}', '', text)  # Remove 30+ unbroken strings
    text = re.sub(r'\s+', ' ', text).strip()  # Collapse mutliple whitespaces
    
    return text

# * Validate text content in email body
def validate_text_amount(text: str):
    
    # * Check text content size
    if not text or len(text) < 10:
        return False
    
    # * Check ratio of printable text
    printable_text = sum(1 for char in text if char.isprintable() or char.isspace())
    ratio = printable_text / len(text)  # Valid to total text percent 
    
    return ratio > 0.7  # Set a threshold (more than 70% has to be valid text)

def extract_email_info(email_id: str):
    
    # * Locate email from ID through API service
    service = connect()
    current_email = service.users().messages().get(
        userId="me", 
        id=email_id,  # Match email with current ID
        format="full"
    ).execute()
    
    # * Validate existance
    if not current_email:
        return "Could not find a matching email."
        
    encoded_email_body = None  # Initialize email body
    mime_type = None  # Initialize text type 

    # * Locate email content from current email
    if "body" in current_email["payload"] and "data" in current_email["payload"]["body"]:
        encoded_email_body = current_email["payload"]["body"]["data"]  # Encoded due to size
        mime_type = current_email["payload"].get("mimeType", "")
    else:
        for part in current_email["payload"]["parts"]:  # Iterate through list (prefer plain text)
            part_mime = part.get("mimeType", "")
            
            # * Look for plain text, then html text after
            if part_mime == "text/plain":  # Check each part's mimeType
                if "body" in part and "data" in part["body"]:
                    encoded_email_body = part["body"]["data"]
                    mime_type = "text/plain"
                    break
            elif part_mime == "text/html" and not encoded_email_body:
                if "body" in part and "data" in part["body"]:
                    encoded_email_body = part["body"]["data"]
                    mime_type = "text/html"
                
    # * Validate email body
    if not encoded_email_body:
        return "Could not extract email body content."
        
    full_email_body = ascii_text_convert(encoded_email_body)  # Decode email body
    
    # * Check for HTML, and extract
    if mime_type == "text/html":
        full_email_body = extract_text_from_html(full_email_body)
        
    # * Validate text ratio
    if not validate_text_amount(full_email_body):
        return "Email contains non-text content."
    
    # * Extract header fields (header contains list of fields)
    headers = current_email["payload"]["headers"]
    subject = next((header["value"] for header in headers if header["name"] == "Subject"), None)
    sender = next((header["value"] for header in headers if header["name"] == "From"), None)
    date = next((header["value"] for header in headers if header["name"] == "Date"), None)
    
    return subject, sender, date, full_email_body

# * Summarize email content based on ID
@tool
def summarize_email(email_id: str):
    """Summarize a single email by its message ID. The email_id must be a string like '19a8f479946bf71e' returned from list_unread_emails tool."""
    
    print("TOOL CALLED: Summarize E-Mail on", email_id)
    
    # * Clean the email ID format
    email_id = email_id.lower().strip()
    
    # # DEBUG: Email ID format
    # print(f"Received email_id type: {type(email_id)}")
    # print(f"Received email_id value: {repr(email_id)}")
    
    # * Extract email contents
    subject, sender, date, full_email_body = extract_email_info(email_id)

    # DEBUG: Email content
    print("="*50)
    print(f"Email ID: {email_id}\n")
    print(f"Subject: {subject}")
    print(f"Sender: {sender}")
    print(f"Date: {date}\n")
    print(f"Body: {full_email_body}")
    print("="*50, "\n")

    # * Create prompt template for LLM
    prompt = (
        "Summarize the following e-mail concisely:\n\n"
        f"Subject: {subject}\n"
        f"Sender: {sender}\n"
        f"Date: {date}\n\n"
        f"Body: {full_email_body}\n"
    )
    
    # * Feed prompt into LLM 
    response = RAW_LLM.invoke(prompt).content 
    
    return response

# * Load the local model
model = init_chat_model(CHAT_MODEL, model_provider="ollama", base_url=BASE_URL)
LLM = model.bind_tools([list_unread_emails, summarize_email])  # Tools for model use

# * Model for basic tasks (summarizing)
RAW_LLM = init_chat_model(CHAT_MODEL, model_provider="ollama", base_url=BASE_URL)

# * Updates the current state
def llm_node(state):
    response = LLM.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

# * Route state conditonally to different notes
def router(state):
    last_message = state["messages"][-1]
    return "tools" if getattr(last_message, "tool_calls", None) else "end"  # Call a tool or end run

# * Define tools
tool_node = ToolNode([list_unread_emails, summarize_email])

builder = StateGraph(ChatState)  # Build initial graph
builder.add_node("LLM", llm_node)  # Create LLM node
builder.add_node("tools", tool_node)  # Create tools node
builder.add_edge(START, "LLM")  # Route from START to LLM
builder.add_edge("LLM", "tools")  # Route from LLM to tools
builder.add_edge("tools", END)  # Route from tools to END
builder.add_conditional_edges("LLM", router, {"tools": "tools", "end": END})  # Compile structure

# * Compile graph with nodes and edges
graph = builder.compile()

if __name__ == "__main__":
    state = {"messages": []}
    
    while True:
        
        print("Type an instruction (q to quit):\n")
        user_message = str(input("> "))
        
        if user_message.lower() == "q":
            break
        
        state["messages"].append({"role": "user", "content": user_message})
        
        state = graph.invoke(state)
        
        answer = state["messages"][-1].content
        print(answer)