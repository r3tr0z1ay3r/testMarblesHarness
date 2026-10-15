"""Data models and schemas for the FastAPI CRUD application."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """Shared properties for an Item."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Title or name of the item",
        examples=["Mechanical Keyboard"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of the item",
        examples=["RGB backlight with mechanical blue switches"],
    )
    price: float = Field(
        ...,
        gt=0,
        description="Price in USD (must be greater than 0)",
        examples=[79.99],
    )
    in_stock: bool = Field(
        default=True,
        description="Whether the item is currently in stock",
        examples=[True],
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags or categories associated with the item",
        examples=[["electronics", "peripherals"]],
    )


class ItemCreate(ItemBase):
    """Schema for creating a new Item."""

    pass


class ItemUpdate(ItemBase):
    """Schema for fully updating (PUT) an existing Item."""

    pass


class ItemPatch(BaseModel):
    """Schema for partially updating (PATCH) an existing Item."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Title or name of the item",
        examples=["Mechanical Keyboard v2"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of the item",
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        description="Price in USD (must be greater than 0)",
        examples=[89.99],
    )
    in_stock: Optional[bool] = Field(
        None,
        description="Whether the item is currently in stock",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags or categories associated with the item",
    )


class ItemResponse(ItemBase):
    """Schema for Item responses returned to clients."""

    id: int = Field(..., description="Unique integer identifier for the item")
    created_at: datetime = Field(..., description="Timestamp when the item was created")
    updated_at: datetime = Field(..., description="Timestamp when the item was last updated")

    model_config = ConfigDict(from_attributes=True)


class PaginatedItemsResponse(BaseModel):
    """Paginated list of items with metadata."""

    total: int = Field(..., description="Total number of items matching query")
    skip: int = Field(..., description="Number of items skipped (offset)")
    limit: int = Field(..., description="Page size limit")
    items: List[ItemResponse] = Field(..., description="List of items for current page")


class MessageResponse(BaseModel):
    """Standard message response."""

    message: str
    detail: Optional[str] = None
