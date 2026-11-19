import os
from fastapi.testclient import TestClient

os.environ["DB_PATH"] = "test_tasks.db"

from main import API_KEY, app, init_db

client = TestClient(app)
HEADERS = {"X-API-Key": API_KEY}


def setup_module():
  if os.path.exists("test_tasks.db"):
    os.remove("test_tasks.db")
  init_db()


def teardown_module():
  if os.path.exists("test_tasks.db"):
    os.remove("test_tasks.db")


def test_health_check():
  res = client.get("/")
  assert res.status_code == 200
  assert res.json()["status"] == "ok"


def test_unauthorized_request():
  res = client.get("/tasks")
  assert res.status_code == 401


def test_validation_error_on_empty_title():
  res = client.post("/tasks", json={"title": ""}, headers=HEADERS)
  assert res.status_code == 422


def test_full_crud_lifecycle():
  # 1. Create
  create_res = client.post(
      "/tasks",
      json={"title": "Finish Module 05", "description": "FastAPI + SQLite API"},
      headers=HEADERS,
  )
  assert create_res.status_code == 201
  created = create_res.json()
  task_id = created["id"]
  assert created["title"] == "Finish Module 05"
  assert created["completed"] is False

  # 2. Read Single
  get_res = client.get(f"/tasks/{task_id}", headers=HEADERS)
  assert get_res.status_code == 200
  assert get_res.json()["id"] == task_id

  # 3. Read List
  list_res = client.get("/tasks", headers=HEADERS)
  assert list_res.status_code == 200
  assert len(list_res.json()) >= 1

  # 4. Update
  upd_res = client.put(
      f"/tasks/{task_id}",
      json={"completed": True, "title": "Completed Module 05"},
      headers=HEADERS,
  )
  assert upd_res.status_code == 200
  assert upd_res.json()["completed"] is True
  assert upd_res.json()["title"] == "Completed Module 05"

  # 5. Delete
  del_res = client.delete(f"/tasks/{task_id}", headers=HEADERS)
  assert del_res.status_code == 204

  # 6. Verify 404 after delete
  missing_res = client.get(f"/tasks/{task_id}", headers=HEADERS)
  assert missing_res.status_code == 404
