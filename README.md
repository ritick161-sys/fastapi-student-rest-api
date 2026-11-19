# Task Manager REST API (FastAPI + SQLite)

A documented RESTful API built with **FastAPI** and **SQLite** for **Module 05: Python Application Development**. It implements structured CRUD endpoints, parameterized SQLite storage, Pydantic schema validation, API Key header authentication, and automated endpoint tests.

## Key Features

- **FastAPI Routing & OpenAPI Docs:** Clean REST endpoints (`GET`, `POST`, `PUT`, `DELETE`) with interactive Swagger UI at `/docs`.
- **SQLite Persistence:** Local relational storage (`tasks.db`) using context-safe connections and parameterized SQL queries.
- **Schema Validation:** Request and response validation powered by Pydantic models (`TaskCreate`, `TaskUpdate`, `TaskOut`).
- **API Key Authentication:** Protected task routes verified via the `X-API-Key` HTTP header.
- **Automated Testing:** Full CRUD, validation, and authorization test suite using `pytest` and FastAPI `TestClient`.

## Project Structure

```text
python-task-manager-api/
├── main.py            # FastAPI application, SQLite logic, schemas, and auth
├── test_main.py       # Automated pytest endpoint tests
├── requirements.txt   # Project dependencies
├── .gitignore         # Ignored virtual environment and database files
└── README.md          # Setup and API documentation
