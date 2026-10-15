"""Thread-safe In-Memory Database for Items."""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.models import ItemCreate, ItemPatch, ItemResponse, ItemUpdate


class InMemoryDatabase:
    """A thread-safe, in-memory repository implementing full CRUD operations."""

    def __init__(self, seed: bool = True) -> None:
        self._lock = threading.RLock()
        self._storage: Dict[int, ItemResponse] = {}
        self._next_id: int = 1
        if seed:
            self.seed_sample_data()

    def create(self, item_in: ItemCreate) -> ItemResponse:
        """Create and store a new item."""
        with self._lock:
            item_id = self._next_id
            self._next_id += 1
            now = datetime.now(timezone.utc)

            item = ItemResponse(
                id=item_id,
                title=item_in.title,
                description=item_in.description,
                price=item_in.price,
                in_stock=item_in.in_stock,
                tags=item_in.tags,
                created_at=now,
                updated_at=now,
            )
            self._storage[item_id] = item
            return item.model_copy()

    def get(self, item_id: int) -> Optional[ItemResponse]:
        """Retrieve an item by its ID."""
        with self._lock:
            item = self._storage.get(item_id)
            return item.model_copy() if item else None

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        in_stock: Optional[bool] = None,
        tag: Optional[str] = None,
    ) -> Tuple[List[ItemResponse], int]:
        """Retrieve a paginated and filtered list of items."""
        with self._lock:
            items = list(self._storage.values())

            # Apply search filter (title or description)
            if search:
                query = search.strip().lower()
                items = [
                    item
                    for item in items
                    if query in item.title.lower()
                    or (item.description and query in item.description.lower())
                ]

            # Apply stock filter
            if in_stock is not None:
                items = [item for item in items if item.in_stock == in_stock]

            # Apply tag filter
            if tag:
                target_tag = tag.strip().lower()
                items = [
                    item
                    for item in items
                    if any(t.lower() == target_tag for t in item.tags)
                ]

            total = len(items)
            paginated = items[skip : skip + limit]
            return [item.model_copy() for item in paginated], total

    def update(self, item_id: int, item_in: ItemUpdate) -> Optional[ItemResponse]:
        """Fully replace an existing item (PUT)."""
        with self._lock:
            existing = self._storage.get(item_id)
            if not existing:
                return None

            now = datetime.now(timezone.utc)
            updated = ItemResponse(
                id=item_id,
                title=item_in.title,
                description=item_in.description,
                price=item_in.price,
                in_stock=item_in.in_stock,
                tags=item_in.tags,
                created_at=existing.created_at,
                updated_at=now,
            )
            self._storage[item_id] = updated
            return updated.model_copy()

    def patch(self, item_id: int, item_in: ItemPatch) -> Optional[ItemResponse]:
        """Partially update an existing item (PATCH)."""
        with self._lock:
            existing = self._storage.get(item_id)
            if not existing:
                return None

            update_data = item_in.model_dump(exclude_unset=True)
            if not update_data:
                # No fields changed, return existing
                return existing.model_copy()

            data = existing.model_dump()
            data.update(update_data)
            data["updated_at"] = datetime.now(timezone.utc)

            updated = ItemResponse(**data)
            self._storage[item_id] = updated
            return updated.model_copy()

    def delete(self, item_id: int) -> bool:
        """Delete an item by its ID."""
        with self._lock:
            if item_id in self._storage:
                del self._storage[item_id]
                return True
            return False

    def count(self) -> int:
        """Return total number of items currently in the database."""
        with self._lock:
            return len(self._storage)

    def clear(self) -> None:
        """Clear all records and reset the autoincrement ID counter."""
        with self._lock:
            self._storage.clear()
            self._next_id = 1

    def seed_sample_data(self) -> None:
        """Seed initial realistic records for exploration."""
        samples = [
            ItemCreate(
                title="Ergonomic Mechanical Keyboard",
                description="Split layout mechanical keyboard with hot-swappable switches",
                price=129.99,
                in_stock=True,
                tags=["electronics", "hardware", "office"],
            ),
            ItemCreate(
                title="Precision Wireless Mouse",
                description="Ultra-lightweight sensor mouse with 70h battery life",
                price=59.50,
                in_stock=True,
                tags=["electronics", "accessories"],
            ),
            ItemCreate(
                title="4K IPS Monitor 27-inch",
                description="Color-accurate USB-C HDR400 display with 99% sRGB coverage",
                price=349.00,
                in_stock=False,
                tags=["monitors", "office"],
            ),
        ]
        for s in samples:
            self.create(s)


# Global singleton instance for application use
db = InMemoryDatabase(seed=True)


def get_db() -> InMemoryDatabase:
    """Dependency provider for FastAPI route injection."""
    return db
