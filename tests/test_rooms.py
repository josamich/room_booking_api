import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_rooms():
    """Test listing all rooms"""
    response = client.get("/rooms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Main Conference Room"


def test_get_room():
    """Test getting a specific room"""
    response = client.get("/rooms/conference-room-1")
    assert response.status_code == 200
    data = response.json()
    assert data["room_id"] == "conference-room-1"
    assert data["name"] == "Main Conference Room"
    assert data["capacity"] == 12


def test_get_nonexistent_room():
    """Test getting a room that doesn't exist"""
    response = client.get("/rooms/nonexistent")
    assert response.status_code == 404


def test_create_room():
    """Test creating a new room"""
    new_room = {
        "name": "Test Room",
        "capacity": 5,
        "description": "Test description"
    }
    response = client.post("/rooms", json=new_room)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Room"
    assert data["capacity"] == 5
    assert "room_id" in data


def test_delete_room_with_no_bookings():
    """Test deleting a room without bookings"""
    # First create a room
    new_room = {"name": "Temporary Room", "capacity": 4}
    create_response = client.post("/rooms", json=new_room)
    room_id = create_response.json()["room_id"]
    
    # Then delete it
    delete_response = client.delete(f"/rooms/{room_id}")
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/rooms/{room_id}")
    assert get_response.status_code == 404
