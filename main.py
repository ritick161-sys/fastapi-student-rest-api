from contextlib import asynccontextmanager, contextmanager
import os
import sqlite3
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

DB_PATH = os.getenv("DB_PATH", "tasks.db")
API_KEY = os.getenv("API_KEY", "codomax-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# --- Database Setup & Connection Helper ---
@contextmanager
def get_db():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  try:
    yield conn
    conn.commit()
  finally:
    conn.close()


def init_db() -> None:
  with get_db() as conn:
    conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                completed BOOLEAN NOT NULL DEFAULT 0
            )
            """)


# --- API Key Authentication Dependency ---
def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
  if api_key != API_KEY:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing X-API-Key header.",
    )
  return api_key


# --- Pydantic Request & Response Schemas ---
class TaskCreate(BaseModel):
  title: str = Field(
      ...,
      min_length=1,
      max_length=120,
      json_schema_extra={"example": "Build REST API"},
  )
  description: str = Field(
      default="",
      max_length=500,
      json_schema_extra={"example": "Implement FastAPI with SQLite"},
  )
  completed: bool = False


class TaskUpdate(BaseModel):
  title: str | None = Field(default=None, min_length=1, max_length=120)
  description: str | None = Field(default=None, max_length=500)
  completed: bool | None = None


class TaskOut(BaseModel):
  id: int
  title: str
  description: str
  completed: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()
  yield


app = FastAPI(
    title="Task Manager REST API",
    description=(
        "Module 05 REST API built with FastAPI, SQLite, Pydantic validation,"
        " and API Key authentication."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# --- Health Check Endpoint ---
@app.get("/", tags=["Health"])
def health_check():
  return {"status": "ok", "message": "Task Manager REST API is running"}


# --- CRUD Endpoints ---
@app.post(
    "/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
    tags=["Tasks"],
)
def create_task(payload: TaskCreate):
  with get_db() as conn:
    cursor = conn.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
        (payload.title.strip(), payload.description.strip(), payload.completed),
    )
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return dict(row)


@app.get(
    "/tasks",
    response_model=list[TaskOut],
    dependencies=[Depends(verify_api_key)],
    tags=["Tasks"],
)
def list_tasks(completed: bool | None = None):
  with get_db() as conn:
    if completed is None:
      rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    else:
      rows = conn.execute(
          "SELECT * FROM tasks WHERE completed = ? ORDER BY id DESC",
          (completed,),
      ).fetchall()
    return [dict(r) for r in rows]


@app.get(
    "/tasks/{task_id}",
    response_model=TaskOut,
    dependencies=[Depends(verify_api_key)],
    tags=["Tasks"],
)
def get_task(task_id: int):
  with get_db() as conn:
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
      raise HTTPException(status_code=404, detail="Task not found.")
    return dict(row)


@app.put(
    "/tasks/{task_id}",
    response_model=TaskOut,
    dependencies=[Depends(verify_api_key)],
    tags=["Tasks"],
)
def update_task(task_id: int, payload: TaskUpdate):
  with get_db() as conn:
    existing = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if not existing:
      raise HTTPException(status_code=404, detail="Task not found.")

    updated_title = (
        payload.title.strip() if payload.title is not None else existing["title"]
    )
    updated_desc = (
        payload.description.strip()
        if payload.description is not None
        else existing["description"]
    )
    updated_done = (
        payload.completed
        if payload.completed is not None
        else bool(existing["completed"])
    )

    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id"
        " = ?",
        (updated_title, updated_desc, updated_done, task_id),
    )
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
    tags=["Tasks"],
)
def delete_task(task_id: int):
  with get_db() as conn:
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
      raise HTTPException(status_code=404, detail="Task not found.")
