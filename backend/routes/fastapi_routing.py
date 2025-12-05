"""
BASIC FASTAPI ROUTE NOTES
Dependencies: fastapi, uvicorn, pydantic
C: Create (POST Method)
R: Read (GET Method)
U: Update (PUT Method)
D: Delete (DELETE Method)
Client -> Request -> Server -> Response -> Client
"""

from fastapi import FastAPI
import uvicorn

from pydantic import BaseModel  # Model used to convert data to JSON for API
from typing import List, Optional  # Built-in for data types (optional)
from uuid import UUID, uuid4  # Built-in to create a unique id

class Task(BaseModel):
    id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    
tasks = []  # Test tasks (local)

# * Instance of app
app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI server is running!"}

@app.post("/tasks/", response_model=Task)  # Location to input tasks and model to convert to JSON
def create_task(task: Task): # Want to except a new task using pydantic model
    task.id = uuid4()  # New unique identifier
    tasks.append(task)
    return task 

# * Simple route (get request)
@app.get("/tasks/", response_model=List[Task])  # List type of all tasks will be returned
def read_tasks():
    return tasks  # Auto converts to JSON data  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Web server to run API (locally)