"""FastAPI Router implementing standard RESTful CRUD operations for Items."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.database import InMemoryDatabase, get_db
from app.models import (
    ItemCreate,
    ItemPatch,
    ItemResponse,
    ItemUpdate,
    MessageResponse,
    PaginatedItemsResponse,
)

router = APIRouter(prefix="/api/items", tags=["Items"])


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Add a new item to the in-memory database.",
)
def create_item(
    item_in: ItemCreate,
    db: InMemoryDatabase = Depends(get_db),
) -> ItemResponse:
    """Create a new item record."""
    created = db.create(item_in)
    return created


@router.get(
    "/",
    response_model=PaginatedItemsResponse,
    summary="List items",
    description="Retrieve items with optional pagination, keyword search, stock status, and tag filtering.",
)
def list_items(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    tag: Optional[str] = Query(None, description="Filter by specific tag"),
    db: InMemoryDatabase = Depends(get_db),
) -> PaginatedItemsResponse:
    """List and filter items."""
    items, total = db.list(skip=skip, limit=limit, search=search, in_stock=in_stock, tag=tag)
    return PaginatedItemsResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID",
    description="Retrieve a single item by its unique ID. Returns 404 if not found.",
)
def get_item(
    item_id: int,
    db: InMemoryDatabase = Depends(get_db),
) -> ItemResponse:
    """Fetch an item by its ID."""
    item = db.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return item


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Replace / update item",
    description="Fully update an existing item by ID. All required fields must be supplied.",
)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: InMemoryDatabase = Depends(get_db),
) -> ItemResponse:
    """Fully replace an existing item."""
    updated = db.update(item_id, item_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return updated


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Partially update item",
    description="Update one or more fields of an existing item by ID. Only provided fields are updated.",
)
def patch_item(
    item_id: int,
    item_in: ItemPatch,
    db: InMemoryDatabase = Depends(get_db),
) -> ItemResponse:
    """Partially update fields of an item."""
    updated = db.patch(item_id, item_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return updated


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item",
    description="Remove an item from the in-memory database. Returns 204 on success or 404 if not found.",
)
def delete_item(
    item_id: int,
    db: InMemoryDatabase = Depends(get_db),
) -> Response:
    """Delete an item by its ID."""
    deleted = db.delete(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/actions/reset",
    response_model=MessageResponse,
    summary="Reset database to seed data",
    description="Clears the database and reseeds standard sample items.",
)
def reset_database(
    db: InMemoryDatabase = Depends(get_db),
) -> MessageResponse:
    """Reset the database to initial state."""
    db.clear()
    db.seed_sample_data()
    return MessageResponse(
        message="Database reset successfully",
        detail=f"Populated with {db.count()} sample items",
    )
