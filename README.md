# Python & FastAPI Fundamentals Guide

A comprehensive guide covering essential Python concepts and FastAPI best practices, complete with a fully functional To-Do List API implementation.

## Table of Contents
- [Python Fundamentals](#python-fundamentals)
  - [Collections](#collections)
  - [Decorators](#decorators)
  - [Async Programming](#async-programming)
  - [Copy Operations](#copy-operations)
  - [Virtual Environments](#virtual-environments)
- [FastAPI & REST API Design](#fastapi--rest-api-design)
  - [Pydantic Models](#pydantic-models)
  - [POST Routes](#post-routes)
  - [HTTP Status Codes](#http-status-codes)
  - [Dependency Injection](#dependency-injection)
  - [CORS Configuration](#cors-configuration)
- [To-Do List API](#fastapi-todo-list-api)
  - [Quick Start](#quick-start)
  - [API Endpoints](#api-endpoints)
  - [Technology Stack](#technology-stack)

---

## Section 1: Python Fundamentals

### 1. Collections

#### List
- **Mutable**, ordered collection of items
- Created using square brackets `[]`
- Elements can be added, removed, or modified
- **Use when**: You need a collection that changes frequently

```python
my_list = [1, 2, 3, "hello"]
my_list.append(4)  # Modifiable
```

#### Tuple
- **Immutable**, ordered collection of items  
- Created using parentheses `()`
- Elements cannot be changed after creation
- **Use when**: You need data integrity and the collection shouldn't change
- **Performance**: Faster than lists for iteration

```python
my_tuple = (1, 2, 3, "hello")
# my_tuple[0] = 5  # This would raise an error
```

#### Dictionary
- **Mutable**, unordered collection of key-value pairs
- Created using curly braces `{}`
- **Fast lookups** by key
- **Use when**: You need to store and retrieve data by unique keys

```python
my_dict = {"name": "John", "age": 30, "city": "New York"}
my_dict["age"] = 31  # Modifiable
```

### 2. Decorators

Functions that modify the behavior of other functions without permanently changing them. They're essentially function wrappers that add functionality.

**FastAPI Route Example:**
```python
from fastapi import FastAPI
import time

def log_execution_time(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.2f} seconds")
        return result
    return wrapper

app = FastAPI()

@app.get("/items/{item_id}")
@log_execution_time
async def read_item(item_id: int):
    # Simulate some processing
    await asyncio.sleep(1)
    return {"item_id": item_id, "name": f"Item {item_id}"}
```

### 3. Async Programming

When you use `async def` in Python:
- The function becomes a **coroutine** that can be paused and resumed
- It must be called with `await`
- Allows other code to run while waiting for I/O operations
- **Doesn't block** the event loop

**Why it's useful for APIs:**
- Handles many **concurrent connections** efficiently
- Better performance for **I/O-bound operations** (database calls, external API calls)
- Scales well with many simultaneous users
- Non-blocking operations improve overall throughput

```python
import asyncio

async def fetch_data():
    # Simulate database call or API request
    await asyncio.sleep(1)
    return {"data": "some result"}

@app.get("/data")
async def get_data():
    result = await fetch_data()
    return result
```

### 4. Copy Operations: deep vs shallow copy

#### Shallow Copy
- Creates a new object but **references the same nested objects**
- Changes to nested objects affect both original and copy
- Created using `copy()` method or `copy.copy()`

#### Deep Copy
- Creates a **completely independent copy** including all nested objects
- Changes to nested objects **don't affect** the original
- Created using `copy.deepcopy()`

```python
import copy

original = [[1, 2], [3, 4]]

# Shallow copy
shallow = original.copy()
shallow[0][0] = 99
print(original)  # [[99, 2], [3, 4]] - original affected!

# Deep copy
deep = copy.deepcopy(original)
deep[0][0] = 100
print(original)  # [[99, 2], [3, 4]] - original unchanged
```

### 5. Virtual Environments

A virtual environment is an **isolated Python environment** that allows you to manage dependencies for different projects separately.

**Why it's important:**
- Prevents conflicts between project dependencies
- Allows different projects to use different package versions
- Makes projects portable and reproducible
- Avoids polluting the system-wide Python installation

**Usage:**
```bash
# Create virtual environment
python -m venv myproject_env

# Activate (Windows)
myproject_env\Scripts\activate

# Activate (Unix/MacOS)
source myproject_env/bin/activate

# Install packages in isolated environment
pip install fastapi uvicorn

# Deactivate when done
deactivate
```

---

## Section 2: FastAPI & REST API Design

### 1. Pydantic Models

Pydantic models are used for:
- **Data validation** and parsing
- **Serialization** and deserialization  
- **API documentation** generation
- **Type hints** enforcement

**Simple Example:**
```python
from pydantic import BaseModel, EmailStr, conint
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr  # Validates email format
    age: conint(gt=0, le=120)  # Constrained integer
    bio: Optional[str] = None  # Optional field
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "bio": "Software developer"
            }
        }
```

### 2. POST Routes

```python
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    age: int

class UserResponse(BaseModel):
    status: str
    message: str
    received_data: UserCreate

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return UserResponse(
        status="success",
        message="User data received successfully",
        received_data=user
    )
```

### 3. HTTP Status Codes

HTTP status codes are standardized codes that indicate the result of an HTTP request.

**Common API Status Codes:**

| Code | Name | Usage |
|------|------|-------|
| `200 OK` | Success | Request succeeded |
| `201 Created` | Resource Created | Resource created successfully |
| `400 Bad Request` | Client Error | Invalid request data |
| `404 Not Found` | Not Found | Resource doesn't exist |

**Examples:**
```python
# 200 OK - Successful GET request
return {"user": user_data}

# 201 Created - Successful POST request  
return user_data, 201

# 400 Bad Request - Invalid input
raise HTTPException(status_code=400, detail="Invalid input data")

# 404 Not Found - Resource not found
raise HTTPException(status_code=404, detail="User not found")
```

### Dependency Injection

Dependency Injection is a pattern where dependencies are provided to functions rather than created within them, making code more testable and modular.

**FastAPI Example:**
```python
from fastapi import FastAPI, Depends, Header, HTTPException

app = FastAPI()

# Dependency function
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization[7:]
    # Verify token logic here
    return {"user_id": 123, "username": "john_doe"}

# Database connection dependency
async def get_database():
    # Simulate database connection
    db = {"host": "localhost", "port": 5432}
    try:
        yield db
    finally:
        # Cleanup code
        pass

@app.get("/protected-data")
async def get_protected_data(
    current_user: dict = Depends(verify_token),
    db: dict = Depends(get_database)
):
    return {
        "message": "This is protected data",
        "user": current_user,
        "database": db
    }
```

### CORS Configuration

CORS (Cross-Origin Resource Sharing) is a security mechanism that allows or restricts resources on a web page to be requested from another domain.

**Why it's important:**
- Prevents malicious websites from making requests to your API
- Allows controlled cross-origin requests when needed
- Essential for web applications with frontend and backend on different domains
- Required for mobile apps and third-party integrations

**FastAPI CORS Setup:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-app.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Or specify: ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],  # Or specify specific headers
)

@app.get("/")
async def main():
    return {"message": "Hello World"}
```

---

## FastAPI To-Do List API

A lightweight, high-performance, in-memory task manager API built with Python, FastAPI, and Pydantic. This application provides a simple yet robust foundation for managing tasks with full CRUD functionality.

### Quick Start

#### Prerequisites
- Python 3.8 or newer

#### Installation & Setup

1. **Clone and setup environment:**
```bash
git clone https://github.com/Thomas1507/fastapi-todo-app.git
cd fastapi-todo-app

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic
```

2. **Run the application:**
```bash
uvicorn main:app --reload --port 8000
```

3. **Access the API documentation:**
   - **Interactive Docs:** http://127.0.0.1:8000/docs
   - **Alternative Docs:** http://127.0.0.1:8000/redoc

### API Endpoints

#### 1. Get All Tasks
```bash
curl -X GET "http://127.0.0.1:8000/tasks"
```
**Response:**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, and eggs",
    "completed": false
  }
]
```

#### 2. Create a New Task
```bash
curl -X POST "http://127.0.0.1:8000/tasks" \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Learn FastAPI", "description": "Read the official documentation"}'
```
**Response (201 Created):**
```json
{
  "id": 2,
  "title": "Learn FastAPI",
  "description": "Read the official documentation",
  "completed": false
}
```

#### 3. Get a Single Task
```bash
curl -X GET "http://127.0.0.1:8000/tasks/1"
```
**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, and eggs",
  "completed": false
}
```

#### 4. Update a Task
```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" \\
  -H "Content-Type: application/json" \\
  -d '{"completed": true}'
```
**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, and eggs",
  "completed": true
}
```

#### 5. Delete a Task
```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```
**Response:** `204 No Content`

### Technology Stack

- **Backend Framework**: FastAPI
- **Data Validation**: Pydantic - Data validation using Python type annotations
- **ASGI Server**: Uvicorn - ASGI server
- **Storage**: In-memory Python list for simplicity

