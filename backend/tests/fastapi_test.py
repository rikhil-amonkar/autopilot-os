"""
***BASIC FASTAPI ROUTE NOTES***
- Dependencies: fastapi, uvicorn, pydantic
- C: Create (POST Method)
  R: Read (GET Method)
  U: Update (PUT Method)
  D: Delete (DELETE Method)
- Client -> Request -> Server -> Response -> Client
- '/docs' -> See curl requests and documentation for FastAPI
"""

from fastapi import FastAPI, HTTPException
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

# * Get home/root page
@app.get("/")
def root():
    return {"message": "FastAPI server is running!"}

# * Add a task
@app.post("/tasks/", response_model=Task)  # Location to input tasks and model to convert to JSON
def create_task(task: Task): # Want to except a new task using pydantic model
    task.id = uuid4()  # New unique identifier
    tasks.append(task)
    return task

# * Simple route (get all tasks)
@app.get("/tasks/", response_model=List[Task])  # List type of all tasks will be returned
def read_tasks():
    return tasks  # Auto converts to JSON data  

# * Read a single task
@app.get("/tasks/{task_id}", response_model=Task)  # Task ID argument
def read_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            return task  # If matching task exists (based on ID) return
        
    return HTTPException(status_code=404, detail="Task not found.")  # Raise 404 error with message if task does not exist

# * Update a task
@app.put("/tasks/{task_id}", response_model=Task)  # Task ID argument
def update_task(task_id: UUID, task_update: Task):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.dict(exclude_unset=True))  # Copy task and update the copy with only changed dict info from new task input
            tasks[index] = updated_task  # Update original task with new version
            
    return HTTPException(status_code=404, detail="Task not found.")  # Raise 404 error with message if task does not exist

# * Delete a task
@app.delete("/tasks/{task_id}", response_model=Task)  # Task ID argument
def delete_task(task_id: UUID):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(index)  # Remove corresponding task based on index
        
    return HTTPException(status_code=404, detail="Task not found.")  # Raise 404 error with message if task does not exist

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Web server to run API (locally)