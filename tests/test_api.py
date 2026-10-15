"""Test suite for FastAPI In-Memory CRUD Server."""

import pytest
from fastapi.testclient import TestClient

from app.database import db
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db_before_each_test():
    """Ensure a clean, predictable database state before every test."""
    db.clear()
    db.seed_sample_data()
    yield


def test_root_and_health():
    """Verify root info endpoint and health check."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert data_root["status"] == "online"
    assert "documentation" in data_root
    assert data_root["items_in_database"] == 3

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
    assert res_health.json()["items_count"] == 3


def test_list_items_default():
    """List items with default pagination."""
    response = client.get("/api/items/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["skip"] == 0
    assert data["limit"] == 50


def test_list_items_pagination():
    """Test pagination skip and limit."""
    response = client.get("/api/items/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 1
    assert data["skip"] == 1
    assert data["limit"] == 1
    assert data["items"][0]["id"] == 2


def test_list_items_filters():
    """Test search, in_stock, and tag filtering."""
    # Search for 'keyboard'
    res_search = client.get("/api/items/?search=keyboard")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["total"] == 1
    assert "Keyboard" in search_data["items"][0]["title"]

    # Filter in_stock=false
    res_stock = client.get("/api/items/?in_stock=false")
    assert res_stock.status_code == 200
    stock_data = res_stock.json()
    assert stock_data["total"] == 1
    assert stock_data["items"][0]["in_stock"] is False

    # Filter by tag
    res_tag = client.get("/api/items/?tag=monitors")
    assert res_tag.status_code == 200
    tag_data = res_tag.json()
    assert tag_data["total"] == 1
    assert "monitors" in tag_data["items"][0]["tags"]


def test_get_item_by_id():
    """Retrieve a single item by ID."""
    response = client.get("/api/items/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert "Keyboard" in item["title"]
    assert "created_at" in item
    assert "updated_at" in item


def test_get_item_not_found():
    """Ensure 404 is returned when item does not exist."""
    response = client.get("/api/items/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_item_success():
    """Test creating a new valid item."""
    new_payload = {
        "title": "Noise-Cancelling Headphones",
        "description": "Over-ear active noise-cancelling wireless headphones",
        "price": 199.99,
        "in_stock": True,
        "tags": ["audio", "wireless", "electronics"],
    }
    response = client.post("/api/items/", json=new_payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 4
    assert created["title"] == new_payload["title"]
    assert created["price"] == 199.99
    assert created["tags"] == new_payload["tags"]
    assert created["created_at"] is not None

    # Verify presence in database count
    assert db.count() == 4


def test_create_item_validation_error():
    """Ensure invalid payloads trigger Pydantic validation errors (422)."""
    # Empty title
    res_empty_title = client.post(
        "/api/items/",
        json={"title": "", "price": 10.0},
    )
    assert res_empty_title.status_code == 422

    # Negative price
    res_neg_price = client.post(
        "/api/items/",
        json={"title": "Valid Title", "price": -5.0},
    )
    assert res_neg_price.status_code == 422

    # Missing price
    res_missing_price = client.post(
        "/api/items/",
        json={"title": "No Price Item"},
    )
    assert res_missing_price.status_code == 422


def test_update_item_put():
    """Fully replace an existing item (PUT)."""
    update_payload = {
        "title": "Upgraded Keyboard RGB Pro",
        "description": "Upgraded with linear red switches",
        "price": 149.99,
        "in_stock": True,
        "tags": ["electronics", "gaming"],
    }
    response = client.put("/api/items/1", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == 1
    assert updated["title"] == update_payload["title"]
    assert updated["price"] == update_payload["price"]
    assert updated["tags"] == ["electronics", "gaming"]

    # Verify 404 for non-existent item
    res_not_found = client.put("/api/items/9999", json=update_payload)
    assert res_not_found.status_code == 404


def test_patch_item():
    """Partially update specific fields of an existing item (PATCH)."""
    original = client.get("/api/items/2").json()

    # Only update price and in_stock
    patch_payload = {
        "price": 49.99,
        "in_stock": False,
    }
    response = client.patch("/api/items/2", json=patch_payload)
    assert response.status_code == 200
    patched = response.json()
    assert patched["id"] == 2
    assert patched["price"] == 49.99
    assert patched["in_stock"] is False
    # Unmodified fields should retain their original values
    assert patched["title"] == original["title"]
    assert patched["description"] == original["description"]
    assert patched["tags"] == original["tags"]

    # Test patch on non-existent item
    res_not_found = client.patch("/api/items/9999", json={"price": 10.0})
    assert res_not_found.status_code == 404


def test_delete_item():
    """Delete an existing item and ensure subsequent fetch fails."""
    # Delete item with id 3
    delete_res = client.delete("/api/items/3")
    assert delete_res.status_code == 204

    # Verify item is gone
    get_res = client.get("/api/items/3")
    assert get_res.status_code == 404

    # Database count decreased
    assert db.count() == 2

    # Second delete returns 404
    delete_again = client.delete("/api/items/3")
    assert delete_again.status_code == 404


def test_reset_endpoint():
    """Test the database reset action endpoint."""
    # Delete all and verify
    client.delete("/api/items/1")
    client.delete("/api/items/2")
    client.delete("/api/items/3")
    assert db.count() == 0

    # Call reset
    reset_res = client.post("/api/items/actions/reset")
    assert reset_res.status_code == 200
    assert db.count() == 3
