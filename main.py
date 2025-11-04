from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

app = FastAPI(title="To-Do List API", description="A simple task manager")

class TaskBase(BaseModel):
    title: str
    description: str
    completed: bool = False

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

    model_config = ConfigDict(extra='ignore')  # Allow extra fields if needed

class Task(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

tasks: list[Task] = []
next_id: list[int] = [1]  # Mutable for thread-safety in simple cases

@app.get("/tasks", response_model=list[Task], status_code=200, summary="Get all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Task, status_code=200, summary="Get a single task")
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", response_model=Task, status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    new_task = Task(id=next_id[0], **task.model_dump())
    tasks.append(new_task)
    next_id[0] += 1
    return new_task

@app.put("/tasks/{task_id}", response_model=Task, status_code=200, summary="Update a task (partial)")
def update_task(task_id: int, task_update: TaskUpdate):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            update_data = task_update.model_dump(exclude_unset=True)
            updated_task = task.model_copy(update=update_data)
            tasks[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Task not found")
