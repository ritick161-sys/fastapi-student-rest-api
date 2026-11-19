# Task Manager REST API (FastAPI + SQLite)

A documented RESTful API built with **FastAPI** and **SQLite** as part of **Module 05: Python Application Development**. It provides full CRUD functionality with Pydantic request/response validation, API key authentication, and automated endpoint tests.

## Features

- **RESTful Routing:** Structured `POST`, `GET`, `PUT`, and `DELETE` endpoints with appropriate HTTP status codes (`201`, `200`, `204`, `401`, `404`).
- **SQLite Persistence:** Local SQLite database (`tasks.db`) managed via context-safe connections and parameterized SQL queries.
- **Schema Validation:** Automatic payload validation and serialization using Pydantic models (`TaskCreate`, `TaskUpdate`, `TaskOut`).
- **API Key Authentication:** Protected endpoints requiring a valid `X-API-Key` header.
- **Interactive API Docs & Testing:** Auto-generated Swagger UI at `/docs` and automated unit/integration tests with `pytest` and `TestClient`.

## Setup & Running Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
