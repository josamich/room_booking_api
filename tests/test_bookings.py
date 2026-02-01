import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app

client = TestClient(app)


def test_create_booking():
    """Test creating a new booking"""
    start = datetime.utcnow() + timedelta(hours=1)
    end = start + timedelta(hours=1)
    
    booking = {
        "room_id": "conference-room-1",
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    
    response = client.post("/book", json=booking)
    assert response.status_code == 200
    data = response.json()
    assert "booking_id" in data
    assert data["room_id"] == "conference-room-1"


def test_create_booking_in_past():
    """Test that booking in the past fails"""
    start = datetime.utcnow() - timedelta(hours=1)
    end = start + timedelta(hours=1)
    
    booking = {
        "room_id": "conference-room-1",
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    
    response = client.post("/book", json=booking)
    assert response.status_code == 400


def test_create_overlapping_booking():
    """Test that overlapping bookings are prevented"""
    start = datetime.utcnow() + timedelta(hours=2)
    end = start + timedelta(hours=1)
    
    booking = {
        "room_id": "meeting-room-2",
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    
    # Create first booking
    response1 = client.post("/book", json=booking)
    assert response1.status_code == 200
    
    # Try to create overlapping booking
    response2 = client.post("/book", json=booking)
    assert response2.status_code == 409


def test_list_bookings():
    """Test listing all bookings"""
    response = client.get("/bookings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_room_bookings():
    """Test listing bookings for a specific room"""
    response = client.get("/bookings/conference-room-1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cancel_booking():
    """Test canceling a booking"""
    # Create a booking first
    start = datetime.utcnow() + timedelta(hours=5)
    end = start + timedelta(hours=1)

    booking = {
        "room_id": "boardroom-3",
        "start": start.isoformat(),
        "end": end.isoformat()
    }

    create_response = client.post("/book", json=booking)
    booking_id = create_response.json()["booking_id"]

    # Cancel it - Use the request method which supports json parameter
    cancel_data = {
        "room_id": "boardroom-3",
        "booking_id": booking_id
    }
    
    cancel_response = client.request("DELETE", "/cancel", json=cancel_data)
    
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "deleted"


def test_find_free_slots():
    """Test finding free time slots"""
    start = datetime.utcnow() + timedelta(hours=10)
    end = start + timedelta(hours=8)
    
    response = client.get(
        f"/free_slots/conference-room-1",
        params={
            "from_time": start.isoformat(),
            "to_time": end.isoformat(),
            "duration_min": 60
        }
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
