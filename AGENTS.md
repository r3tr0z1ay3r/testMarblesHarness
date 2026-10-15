# AGENTS.md

Instructions, conventions, and architectural guidelines for AI agents working in this repository.

---

## 1. Repository Overview

This repository is a lightweight, production-grade **FastAPI CRUD server** backed by a thread-safe **In-Memory Database**. It is designed for rapid prototyping, local harness testing, and mock service environments with zero external database dependencies.

- **Framework**: FastAPI (using Starlette and Pydantic v2)
- **ASGI Server**: Uvicorn
- **Database**: Thread-safe in-memory dictionary repository (`app.database.InMemoryDatabase`)
- **Default Port**: `8765`
- **Testing Framework**: Pytest + HTTPX (`TestClient`)

---

## 2. Directory & Component Layout

```text
.
├── AGENTS.md            # Guidelines and context for AI agents
├── README.md            # User-facing documentation & cURL examples
├── requirements.txt     # Python runtime and test dependencies
├── start.sh             # Self-bootstrapping launch script (venv + pip + uvicorn)
├── main.py              # Root convenience script (`python main.py`)
├── app/
│   ├── __init__.py      # Package initialization & version
│   ├── database.py      # InMemoryDatabase class with thread-safe CRUD & seeding
│   ├── models.py        # Pydantic v2 data models, validation rules, and responses
│   ├── routes.py        # APIRouter defining REST endpoints (/api/items/...)
│   └── main.py          # FastAPI application factory, CORS, health & root routes
└── tests/
    ├── __init__.py      # Test package initialization
    └── test_api.py      # Automated test suite (12+ tests)
```

---

## 3. Core Architecture & Patterns

### 3.1 In-Memory Database (`app/database.py`)
- **Thread Safety**: Uses `threading.RLock()` across all mutations and reads to guarantee safety across asynchronous event loop contexts and thread pools.
- **Identity & Time**:
  - `_next_id`: Autoincrementing integer primary keys starting at `1`.
  - `created_at` & `updated_at`: UTC timestamps (`datetime.now(timezone.utc)`).
- **CRUD Operations**:
  - `create(item_in: ItemCreate) -> ItemResponse`
  - `get(item_id: int) -> Optional[ItemResponse]`
  - `list(skip, limit, search, in_stock, tag) -> Tuple[List[ItemResponse], int]`
  - `update(item_id: int, item_in: ItemUpdate) -> Optional[ItemResponse]` (PUT / full replace)
  - `patch(item_id: int, item_in: ItemPatch) -> Optional[ItemResponse]` (PATCH / partial update)
  - `delete(item_id: int) -> bool`
  - `clear()` & `seed_sample_data()` for testing and reset capability.
- **Dependency Injection**: Use `get_db()` dependency in route handlers rather than referencing the singleton directly.

### 3.2 Schemas & Models (`app/models.py`)
- Built using **Pydantic v2**.
- `ItemBase`: Shared attributes (`title`, `description`, `price`, `in_stock`, `tags`).
- `ItemCreate`: Inherits `ItemBase`.
- `ItemUpdate`: Full update schema.
- `ItemPatch`: Partial update with all optional fields.
- `ItemResponse`: Includes `id`, `created_at`, `updated_at`, with `ConfigDict(from_attributes=True)`.
- `PaginatedItemsResponse`: Envelope containing `total`, `skip`, `limit`, and `items`.

### 3.3 Routing (`app/routes.py`)
All domain routes are mounted under prefix `/api/items`:
- `POST   /api/items/`               -> `201 Created`
- `GET    /api/items/`               -> `200 OK` (supports `skip`, `limit`, `search`, `in_stock`, `tag`)
- `GET    /api/items/{id}`           -> `200 OK` / `404 Not Found`
- `PUT    /api/items/{id}`           -> `200 OK` / `404 Not Found`
- `PATCH  /api/items/{id}`           -> `200 OK` / `404 Not Found`
- `DELETE /api/items/{id}`           -> `204 No Content` / `404 Not Found`
- `POST   /api/items/actions/reset`  -> `200 OK` (resets to initial seed state)

---

## 4. Environment & Execution Guidelines for Agents

### 4.1 Python Environment
- The repository uses a dedicated virtual environment located at `.venv/`.
- Always target the virtual environment binaries:
  ```bash
  .venv/bin/python ...
  .venv/bin/pip ...
  .venv/bin/pytest ...
  .venv/bin/uvicorn ...
  ```

### 4.2 Starting the Application
Agents should use [start.sh](file:///Users/mako/Mukesh_Workspace/Projects/Extras%26Test/Marbles%20Harness/Code/TestRepo/testMarblesHarness/start.sh) or direct invocation:
```bash
# Via bootstrapping script (automatically configures venv/deps):
./start.sh

# Or directly:
PORT=8765 .venv/bin/python main.py
```

### 4.3 Testing
Before committing any changes, **always** run the pytest suite and verify 100% pass rate:
```bash
.venv/bin/pytest -v
```

---

## 5. Coding Standards & Behavioral Rules

1. **Maintain Thread Safety**: Whenever adding or modifying methods in `InMemoryDatabase`, wrap operations inside `with self._lock:`.
2. **Preserve Immutability on Read**: Always return copies (`model_copy()`) from database getters so callers cannot mutate the in-memory cache directly without using the update methods.
3. **UTC Datetime Enforcement**: Always use timezone-aware UTC timestamps (`datetime.now(timezone.utc)`).
4. **Validation Integrity**: Use Pydantic `Field(...)` constraints (e.g., `gt=0`, `min_length=1`) for domain integrity.
5. **Route Error Handling**: Use standard `fastapi.HTTPException` with appropriate status codes (`404` for non-existent items, `422` for unprocessable entities).
6. **Preserve Documentation & Comments**: Keep docstrings and types up to date. Use `from __future__ import annotations`.
