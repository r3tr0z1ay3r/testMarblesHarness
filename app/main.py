"""FastAPI Application Entry Point."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import db
from app.routes import router

app = FastAPI(
    title="FastAPI In-Memory CRUD Server",
    description=(
        "A fast, modern RESTful CRUD API powered by FastAPI and a thread-safe "
        "In-Memory Database. Demonstrates Create, Read (List & Single), Update (PUT & PATCH), "
        "and Delete operations with Pydantic validation, filtering, and pagination."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for browser / frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Item routes
app.include_router(router)


@app.get("/", tags=["General"], summary="API Root & Overview")
def root() -> JSONResponse:
    """Root endpoint with quick overview and documentation links."""
    return JSONResponse(
        content={
            "app": "FastAPI In-Memory CRUD Server",
            "version": "1.0.0",
            "status": "online",
            "items_in_database": db.count(),
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json",
            },
            "endpoints": {
                "list_or_create_items": "/api/items/",
                "item_by_id": "/api/items/{id}",
                "reset_database": "/api/items/actions/reset",
                "health_check": "/health",
            },
        }
    )


@app.get("/health", tags=["General"], summary="Health Check")
def health_check() -> dict:
    """Service health and database count check."""
    return {
        "status": "healthy",
        "database": "in-memory",
        "items_count": db.count(),
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
