# FastAPI In-Memory CRUD Server

A lightweight, robust RESTful CRUD API server built with **FastAPI** and a thread-safe **In-Memory Database**, featuring data validation via **Pydantic v2**, automatic OpenAPI interactive documentation, and comprehensive automated tests.

---

## Features

- **Full CRUD Operations**:
  - `POST /api/items/` — Create new items with strict schema validation.
  - `GET /api/items/` — List items with pagination (`skip`, `limit`) and filtering (`search`, `in_stock`, `tag`).
  - `GET /api/items/{id}` — Fetch individual item by ID (with 404 handling).
  - `PUT /api/items/{id}` — Full replacement update.
  - `PATCH /api/items/{id}` — Partial field update.
  - `DELETE /api/items/{id}` — Delete item with `204 No Content` response.
- **In-Memory Database**:
  - Thread-safe using `threading.RLock` to prevent race conditions during concurrent requests.
  - Automatic autoincrement ID sequence and UTC timestamping (`created_at`, `updated_at`).
  - Pre-seeded with sample data for immediate exploration.
  - Includes a reset action endpoint (`POST /api/items/actions/reset`) for testing.
- **Interactive Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`.
- **CORS Enabled**: Ready out of the box for frontend/browser consumption.
- **Full Test Suite**: 12 comprehensive unit and integration tests covering positive flows, validation errors, and edge cases.

---

## Project Structure

```text
.
├── app/
│   ├── __init__.py      # App package marker
│   ├── database.py      # Thread-safe in-memory database implementation
│   ├── models.py        # Pydantic models for validation and responses
│   ├── routes.py        # RESTful API route handlers
│   └── main.py          # FastAPI application entrypoint
├── tests/
│   ├── __init__.py      # Tests package marker
│   └── test_api.py      # Automated Pytest suite
├── main.py              # Root runner script (python main.py)
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## Quickstart

### 1. Set Up Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server

You can run the server using either method:

**Option A: Direct python runner**
```bash
python main.py
```

**Option B: Using Uvicorn CLI**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once running, access the server:
- **API Overview & Status**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## API Endpoints & cURL Examples

### 1. Create an Item (POST)
```bash
curl -X POST http://127.0.0.1:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mechanical Keyboard",
    "description": "RGB backlight with tactile switches",
    "price": 89.99,
    "in_stock": true,
    "tags": ["electronics", "peripherals"]
  }'
```

### 2. List Items with Filtering & Pagination (GET)
```bash
# List all items
curl http://127.0.0.1:8000/api/items/

# Search and filter by stock
curl "http://127.0.0.1:8000/api/items/?search=keyboard&in_stock=true"

# Paginate (skip first, limit 2)
curl "http://127.0.0.1:8000/api/items/?skip=1&limit=2"

# Filter by tag
curl "http://127.0.0.1:8000/api/items/?tag=office"
```

### 3. Get Item by ID (GET)
```bash
curl http://127.0.0.1:8000/api/items/1
```

### 4. Full Update (PUT)
```bash
curl -X PUT http://127.0.0.1:8000/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pro Mechanical Keyboard",
    "description": "Upgraded with silent switches",
    "price": 109.99,
    "in_stock": true,
    "tags": ["electronics", "premium"]
  }'
```

### 5. Partial Update (PATCH)
```bash
curl -X PATCH http://127.0.0.1:8000/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 99.99,
    "in_stock": false
  }'
```

### 6. Delete an Item (DELETE)
```bash
curl -X DELETE http://127.0.0.1:8000/api/items/1 -i
```

### 7. Reset In-Memory Database (POST)
```bash
curl -X POST http://127.0.0.1:8000/api/items/actions/reset
```

---

## Running the Automated Tests

Run the test suite with `pytest`:

```bash
pytest -v
```
